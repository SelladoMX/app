"""Tests para PDFSigner (sin red: el TSA es local)"""

import base64
from datetime import UTC, datetime, timedelta
from io import BytesIO
from unittest.mock import MagicMock

import pytest
from asn1crypto import keys as asn1_keys
from asn1crypto import tsp
from asn1crypto import x509 as asn1_x509
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID
from pyhanko.pdf_utils import generic
from pyhanko.pdf_utils.reader import PdfFileReader
from pyhanko.pdf_utils.writer import PageObject, PdfFileWriter
from pyhanko.sign.timestamps import TimeStamper
from pyhanko.sign.timestamps.dummy_client import DummyTimeStamper

from selladomx.errors import PDFError, TSAResponseError, TSAUnavailableError
from selladomx.signing import pdf_signer as pdf_signer_module
from selladomx.signing.pdf_signer import (
    SIGNATURE_BYTES_RESERVED,
    PDFSigner,
    signed_output_path,
)
from selladomx.signing.tsa import APITimeStamper


def _self_signed(cn: str, eku=None):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, cn)])
    now = datetime.now(UTC)
    builder = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(days=1))
        .not_valid_after(now + timedelta(days=30))
    )
    if eku:
        builder = builder.add_extension(x509.ExtendedKeyUsage(eku), critical=True)
    return builder.sign(key, hashes.SHA256()), key


@pytest.fixture(scope="module")
def signer_identity():
    return _self_signed("PERSONA DE PRUEBA")


@pytest.fixture(scope="module")
def tsa_identity():
    return _self_signed("TSA DE PRUEBA", eku=[ExtendedKeyUsageOID.TIME_STAMPING])


class OfflineTSA(DummyTimeStamper):
    """Local TSA that fails the test if pyhanko asks it for a dummy response."""

    def __init__(self, tsa_identity):
        cert, key = tsa_identity
        super().__init__(
            tsa_cert=asn1_x509.Certificate.load(
                cert.public_bytes(serialization.Encoding.DER)
            ),
            tsa_key=asn1_keys.PrivateKeyInfo.load(
                key.private_bytes(
                    serialization.Encoding.DER,
                    serialization.PrivateFormat.PKCS8,
                    serialization.NoEncryption(),
                )
            ),
        )
        self.requests = 0

    async def async_request_tsa_response(self, req):
        self.requests += 1
        return await super().async_request_tsa_response(req)

    async def async_dummy_response(self, md_algorithm):
        raise AssertionError("signature size estimation must not request a timestamp")


def _blank_pdf(path):
    writer = PdfFileWriter()
    stream = writer.add_object(generic.StreamObject(stream_data=b""))
    writer.insert_page(PageObject(contents=stream, media_box=[0, 0, 612, 792]))
    out = BytesIO()
    writer.write(out)
    path.write_bytes(out.getvalue())
    return path


@pytest.fixture
def pdf(tmp_path):
    return _blank_pdf(tmp_path / "contrato.pdf")


def _signer(signer_identity, **kwargs):
    cert, key = signer_identity
    return PDFSigner(cert, key, **kwargs)


class TestSigning:
    def test_free_signing_makes_no_estimation_request(
        self, signer_identity, tsa_identity, pdf
    ):
        tsa = OfflineTSA(tsa_identity)
        tsa_client = MagicMock()
        tsa_client.get_timestamper.return_value = tsa

        output = _signer(signer_identity, tsa_client=tsa_client).sign_pdf(pdf)

        assert output.name == "contrato_firmado.pdf"
        assert tsa.requests == 1
        assert PDFSigner.verify_signature(output) is True

    def test_signature_contents_use_reserved_size(
        self, signer_identity, tsa_identity, pdf
    ):
        output = _signer(
            signer_identity, timestamper=OfflineTSA(tsa_identity)
        ).sign_pdf(pdf)
        with open(output, "rb") as f:
            sig = PdfFileReader(f).embedded_signatures[0]
            assert len(sig.sig_object["/Contents"].original_bytes) * 2 == (
                SIGNATURE_BYTES_RESERVED
            )

    def test_professional_signing_spends_exactly_one_request(
        self, signer_identity, tsa_identity, pdf
    ):
        certum = OfflineTSA(tsa_identity)
        calls = []

        def request_tsa_sign(tsa_req_b64, **kwargs):
            calls.append(kwargs["filename"])
            req = tsp.TimeStampReq.load(base64.b64decode(tsa_req_b64))
            resp = certum.request_tsa_response(req)
            return {
                "tsa_resp_b64": base64.b64encode(resp.dump()).decode(),
                "record_id": "rec-1",
                "verification_url": "https://selladomx.com/v/abc",
                "credits_remaining": 9,
            }

        api_client = MagicMock()
        api_client.request_tsa_sign.side_effect = request_tsa_sign
        stamper = APITimeStamper(api_client, pdf.name, pdf.stat().st_size)

        output = _signer(signer_identity, timestamper=stamper).sign_pdf(pdf)

        assert calls == ["contrato.pdf"]
        assert stamper.record_id == "rec-1"
        assert stamper.credits_remaining == 9
        assert PDFSigner.verify_signature(output) is True

    def test_professional_invalid_response_is_typed(self, signer_identity, pdf):
        rejection_der = bytes.fromhex("30053003020102")  # PKIStatus rejection
        api_client = MagicMock()
        api_client.request_tsa_sign.return_value = {
            "tsa_resp_b64": base64.b64encode(rejection_der).decode(),
            "record_id": "rec-1",
        }
        stamper = APITimeStamper(api_client, pdf.name, 1)

        with pytest.raises(TSAResponseError):
            _signer(signer_identity, timestamper=stamper).sign_pdf(pdf)

    def test_tsa_errors_propagate_unwrapped(self, signer_identity, pdf):
        class Unreachable(TimeStamper):
            async def async_timestamp(self, message_digest, md_algorithm):
                raise TSAUnavailableError()

        tsa_client = MagicMock()
        tsa_client.get_timestamper.return_value = Unreachable()

        with pytest.raises(TSAUnavailableError):
            _signer(signer_identity, tsa_client=tsa_client).sign_pdf(pdf)
        assert not (pdf.parent / "contrato_firmado.pdf").exists()

    def test_does_not_overwrite_existing_signed_copy(
        self, signer_identity, tsa_identity, pdf
    ):
        existing = pdf.parent / "contrato_firmado.pdf"
        existing.write_bytes(b"keep me")
        signer = _signer(signer_identity, timestamper=OfflineTSA(tsa_identity))

        first = signer.sign_pdf(pdf)
        second = signer.sign_pdf(pdf)

        assert existing.read_bytes() == b"keep me"
        assert first.name == "contrato_firmado (1).pdf"
        assert second.name == "contrato_firmado (2).pdf"

    def test_corrupt_pdf_raises_pdf_error(self, signer_identity, tmp_path):
        bad = tmp_path / "roto.pdf"
        bad.write_bytes(b"not a pdf")
        with pytest.raises(PDFError):
            _signer(signer_identity).sign_pdf(bad)

    def test_missing_pdf(self, signer_identity, tmp_path):
        with pytest.raises(PDFError, match="no encontrado"):
            _signer(signer_identity).sign_pdf(tmp_path / "nope.pdf")


class TestOutputPath:
    def test_default_and_output_dir(self, tmp_path):
        src = tmp_path / "a" / "x.pdf"
        assert signed_output_path(src) == tmp_path / "a" / "x_firmado.pdf"
        assert signed_output_path(src, tmp_path) == tmp_path / "x_firmado.pdf"

    def test_gives_up_instead_of_looping_forever(self, tmp_path, monkeypatch):
        monkeypatch.setattr(pdf_signer_module, "MAX_OUTPUT_NAME_ATTEMPTS", 3)
        for name in ["x_firmado.pdf"] + [f"x_firmado ({i}).pdf" for i in (1, 2, 3)]:
            (tmp_path / name).touch()
        with pytest.raises(PDFError):
            signed_output_path(tmp_path / "x.pdf")


class TestVerifySignature:
    def test_unsigned_pdf_is_not_valid(self, pdf):
        assert PDFSigner.verify_signature(pdf) is False

    def test_tampered_pdf_is_not_valid(self, signer_identity, tsa_identity, pdf):
        output = _signer(
            signer_identity, timestamper=OfflineTSA(tsa_identity)
        ).sign_pdf(pdf)
        data = bytearray(output.read_bytes())
        index = data.index(b"/MediaBox")
        data[index + 1 : index + 2] = b"X"
        output.write_bytes(bytes(data))

        assert PDFSigner.verify_signature(output) is False

    def test_missing_file(self, tmp_path):
        with pytest.raises(PDFError):
            PDFSigner.verify_signature(tmp_path / "nope.pdf")


@pytest.mark.network
def test_sign_with_real_free_tsa(signer_identity, pdf):
    from selladomx.signing.tsa import TSAClient

    output = _signer(signer_identity, tsa_client=TSAClient()).sign_pdf(pdf)
    assert PDFSigner.verify_signature(output) is True
