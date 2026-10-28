"""End-to-end tests: load an e.firma, sign a PDF and validate the signature."""

from datetime import UTC, datetime, timedelta

import pytest
from asn1crypto import x509 as asn1_x509
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from pyhanko.pdf_utils.reader import PdfFileReader
from pyhanko.sign.validation import validate_pdf_signature
from pyhanko_certvalidator import ValidationContext

from selladomx.errors import CertificateError
from selladomx.signing.certificate_validator import CertificateValidator
from selladomx.signing.pdf_signer import PDFSigner
from selladomx.signing.tsa import TSAClient


def _load_efirma(efirma_files):
    validator = CertificateValidator(
        efirma_files.cert_path, efirma_files.key_path, efirma_files.password
    )
    return validator.validate_all()


def _validate_single_signature(pdf_path, ca_cert):
    """Validate the only signature in pdf_path, trusting the test CA."""
    trust_root = asn1_x509.Certificate.load(
        ca_cert.public_bytes(serialization.Encoding.DER)
    )
    with open(pdf_path, "rb") as f:
        reader = PdfFileReader(f)
        assert len(reader.embedded_signatures) == 1
        return validate_pdf_signature(
            reader.embedded_signatures[0],
            signer_validation_context=ValidationContext(trust_roots=[trust_root]),
        )


def test_certificate_validator_loads_efirma(efirma_files):
    """The DER .cer and encrypted PKCS#8 .key load with the right password."""
    cert, private_key = _load_efirma(efirma_files)

    serial = cert.subject.get_attributes_for_oid(x509.NameOID.SERIAL_NUMBER)
    assert serial[0].value == "XAXX010101HDFXXX01"
    assert private_key.public_key().public_numbers() == (
        cert.public_key().public_numbers()
    )


def test_certificate_validator_rejects_wrong_password(efirma_files):
    validator = CertificateValidator(
        efirma_files.cert_path, efirma_files.key_path, "incorrecta"
    )
    with pytest.raises(CertificateError):
        validator.validate_all()


def test_sign_pdf_without_timestamp(efirma_files, sample_pdf, tmp_path):
    """Offline signing (no TSA) produces a valid, intact signature.

    Trust (status.bottom_line) is not asserted: asn1crypto types
    x500UniqueIdentifier as a BIT STRING, so path building fails on a subject
    that carries the RFC there as a string, as SAT certificates do.
    """
    cert, private_key = _load_efirma(efirma_files)
    output_path = tmp_path / "signed.pdf"

    result_path = PDFSigner(cert, private_key).sign_pdf(sample_pdf, output_path)

    assert result_path == output_path
    assert result_path.read_bytes().startswith(b"%PDF")
    assert result_path.stat().st_size > sample_pdf.stat().st_size

    status = _validate_single_signature(result_path, efirma_files.ca_cert)
    assert status.intact
    assert status.valid
    assert status.timestamp_validity is None


@pytest.mark.network
def test_sign_pdf_with_free_tsa(efirma_files, sample_pdf, tmp_path):
    """Signing with the free TSA providers embeds a signature timestamp."""
    cert, private_key = _load_efirma(efirma_files)
    output_path = tmp_path / "signed_tsa.pdf"

    PDFSigner(cert, private_key, TSAClient()).sign_pdf(sample_pdf, output_path)

    status = _validate_single_signature(output_path, efirma_files.ca_cert)
    assert status.intact
    assert status.valid
    assert status.timestamp_validity is not None
    assert status.timestamp_validity.intact


def test_tsa_client_initialization():
    """Test that TSA client can be initialized."""
    tsa_client = TSAClient()
    assert tsa_client is not None

    from selladomx.config import TSA_FREE_PROVIDERS

    assert len(TSA_FREE_PROVIDERS) > 0, "No free TSA providers configured"


def test_pdf_signer_requires_certificate():
    """Test that PDF signer requires valid certificate and key."""
    # Constructor only; signing would need a valid cert/key.
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    subject = issuer = x509.Name(
        [
            x509.NameAttribute(x509.oid.NameOID.COMMON_NAME, "Test"),
        ]
    )

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(UTC))
        .not_valid_after(datetime.now(UTC) + timedelta(days=1))
        .sign(private_key, hashes.SHA256())
    )

    tsa_client = TSAClient()
    signer = PDFSigner(cert, private_key, tsa_client)

    assert signer.cert is not None
    assert signer.private_key is not None
    assert signer.tsa_client is not None
