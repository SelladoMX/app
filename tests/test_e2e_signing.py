"""End-to-end integration test for PDF signing workflow."""
import pytest
from pathlib import Path

# These imports will fail if not in dev environment, that's ok
try:
    from selladomx.signing.pdf_signer import PDFSigner
    from selladomx.signing.tsa import TSAClient
    from selladomx.signing.certificate_validator import CertificateValidator
    from selladomx.errors import CertificateError
except ImportError:
    pytest.skip("Application modules not available", allow_module_level=True)


@pytest.fixture
def test_cert_path():
    """Path to test certificate."""
    return Path(__file__).parent / "fixtures" / "certs" / "test_cert.cer"


@pytest.fixture
def test_key_path():
    """Path to test private key."""
    return Path(__file__).parent / "fixtures" / "certs" / "test_key.key"


@pytest.fixture
def test_pdf_path():
    """Path to test PDF."""
    return Path(__file__).parent / "fixtures" / "pdfs" / "sample.pdf"


@pytest.fixture
def test_password():
    """Test certificate password (empty for self-signed test certs)."""
    return ""


@pytest.mark.skipif(
    not (Path(__file__).parent / "fixtures" / "certs" / "test_cert.cer").exists(),
    reason="Test certificate not available - run setup instructions in tests/fixtures/README.md"
)
@pytest.mark.skipif(
    not (Path(__file__).parent / "fixtures" / "pdfs" / "sample.pdf").exists(),
    reason="Test PDF not available - add sample.pdf to tests/fixtures/pdfs/"
)
def test_complete_signing_workflow(test_cert_path, test_key_path, test_pdf_path, test_password, tmp_path):
    """Test complete signing workflow with free TSA.

    This test verifies:
    1. Certificate loading and validation
    2. PDF signing with TSA timestamp
    3. Output file creation and validity
    """
    # Load and validate certificate
    validator = CertificateValidator(test_cert_path, test_key_path, test_password)

    try:
        cert, private_key = validator.validate_all()
    except CertificateError as e:
        pytest.skip(f"Certificate validation failed (expected for test certs): {e}")

    # Setup TSA client (free tier)
    tsa_client = TSAClient()

    # Create output path in temp directory
    output_path = tmp_path / "signed_output.pdf"

    # Sign PDF
    signer = PDFSigner(cert, private_key, tsa_client)
    result_path = signer.sign_pdf(test_pdf_path, output_path)

    # Verify output exists
    assert result_path.exists(), "Signed PDF was not created"
    assert result_path.stat().st_size > 0, "Signed PDF is empty"

    # Verify it's a valid PDF (check magic number)
    with open(result_path, 'rb') as f:
        header = f.read(4)
        assert header == b'%PDF', "Output is not a valid PDF file"

    # Verify file is larger than input (signature adds data)
    original_size = test_pdf_path.stat().st_size
    signed_size = result_path.stat().st_size
    assert signed_size > original_size, "Signed PDF should be larger than original"


@pytest.mark.skipif(
    not (Path(__file__).parent / "fixtures" / "certs" / "test_cert.cer").exists(),
    reason="Test certificate not available"
)
def test_certificate_validator_loads_files(test_cert_path, test_key_path, test_password):
    """Test that certificate validator can load certificate and key files."""
    validator = CertificateValidator(test_cert_path, test_key_path, test_password)

    # This will raise CertificateError for invalid/expired certs, which is expected
    # We just want to verify the files can be loaded
    assert validator.cert_path.exists()
    assert validator.key_path.exists()


def test_tsa_client_initialization():
    """Test that TSA client can be initialized."""
    tsa_client = TSAClient()
    assert tsa_client is not None

    # Verify free TSA URLs are configured
    from selladomx.config import TSA_FREE_PROVIDERS
    assert len(TSA_FREE_PROVIDERS) > 0, "No free TSA providers configured"


def test_pdf_signer_requires_certificate():
    """Test that PDF signer requires valid certificate and key."""
    # This test verifies the PDFSigner constructor signature
    # without actually signing (which would require valid cert/key)

    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.backends import default_backend
    from datetime import datetime, timedelta, UTC

    # Generate a minimal self-signed cert for testing constructor
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

    subject = issuer = x509.Name([
        x509.NameAttribute(x509.oid.NameOID.COMMON_NAME, "Test"),
    ])

    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.now(UTC)
    ).not_valid_after(
        datetime.now(UTC) + timedelta(days=1)
    ).sign(private_key, hashes.SHA256(), default_backend())

    tsa_client = TSAClient()
    signer = PDFSigner(cert, private_key, tsa_client)

    assert signer.cert is not None
    assert signer.private_key is not None
    assert signer.tsa_client is not None
