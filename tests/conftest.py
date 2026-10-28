"""Shared fixtures: isolated QSettings and generated e.firma/PDF fixtures."""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
import PySide6.QtCore
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

_RealQSettings = PySide6.QtCore.QSettings


class _IsolatedQSettings(_RealQSettings):
    """QSettings that always uses IniFormat, so tests can redirect it to tmp.

    On macOS, QSettings.setPath() does not affect NativeFormat (CFPreferences),
    so QSettings("SelladoMX", "SelladoMX") would write the user's real plist.
    """

    def __init__(self, *args, **kwargs):
        ini = _RealQSettings.Format.IniFormat
        if args and isinstance(args[0], str):
            if len(args) < 2 or isinstance(args[1], str):
                args = (ini, _RealQSettings.Scope.UserScope, *args)
        elif args and isinstance(args[0], _RealQSettings.Scope):
            args = (ini, *args)
        elif args and args[0] == _RealQSettings.Format.NativeFormat:
            args = (ini, *args[1:])
        super().__init__(*args, **kwargs)


# Must run before any test module imports selladomx, which binds QSettings
# with `from PySide6.QtCore import QSettings` at import time.
PySide6.QtCore.QSettings = _IsolatedQSettings
_IsolatedQSettings.setDefaultFormat(_RealQSettings.Format.IniFormat)


def _native_settings_file() -> Path:
    return Path(_RealQSettings("SelladoMX", "SelladoMX").fileName())


def _mtime(path: Path):
    return path.stat().st_mtime_ns if path.exists() else None


@pytest.fixture(scope="session", autouse=True)
def _guard_real_settings():
    """Fail the run if the user's real SelladoMX settings were modified."""
    real_file = _native_settings_file()
    before = _mtime(real_file)
    yield
    assert _mtime(real_file) == before, f"Tests modified {real_file}"


@pytest.fixture(autouse=True)
def isolated_settings(tmp_path):
    """Point all QSettings (IniFormat, both scopes) at a per-test directory."""
    settings_dir = tmp_path / "qsettings"
    settings_dir.mkdir()
    for scope in (_RealQSettings.Scope.UserScope, _RealQSettings.Scope.SystemScope):
        _RealQSettings.setPath(
            _RealQSettings.Format.IniFormat, scope, str(settings_dir)
        )
    return settings_dir


# ============================================================================
# e.firma and PDF fixtures
# ============================================================================


@dataclass(frozen=True)
class EFirmaFiles:
    cert_path: Path
    key_path: Path
    password: str
    ca_cert: x509.Certificate


def _minimal_pdf() -> bytes:
    """Build a one-page PDF with a correct xref table."""
    content = b"BT /F1 24 Tf 72 720 Td (SelladoMX test) Tj ET"
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
        b"<< /Length %d >>\nstream\n%s\nendstream" % (len(content), content),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out = bytearray(b"%PDF-1.7\n")
    offsets = []
    for number, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += b"%d 0 obj\n%s\nendobj\n" % (number, body)
    xref_offset = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objects) + 1)
    for offset in offsets:
        out += b"%010d 00000 n \n" % offset
    out += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (
        len(objects) + 1,
        xref_offset,
    )
    return bytes(out)


def _key_usage(**enabled) -> x509.KeyUsage:
    flags = dict.fromkeys(
        [
            "digital_signature",
            "content_commitment",
            "key_encipherment",
            "data_encipherment",
            "key_agreement",
            "key_cert_sign",
            "crl_sign",
            "encipher_only",
            "decipher_only",
        ],
        False,
    )
    flags.update(enabled)
    return x509.KeyUsage(**flags)


@pytest.fixture(scope="session")
def efirma_files(tmp_path_factory) -> EFirmaFiles:
    """Test e.firma issued by a test CA, with a SAT-like subject.

    Written like a SAT e.firma: DER `.cer` and a password-encrypted PKCS#8 DER
    `.key`. The subject carries the RFC in x500UniqueIdentifier as a string;
    asn1crypto can't parse that, and pyhanko_certvalidator rejects such a
    certificate as a trust root, so the leaf is issued by a separate CA.
    """
    directory = tmp_path_factory.mktemp("efirma")
    password = "Prueba1234"
    now = datetime.now(UTC)

    ca_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    ca_name = x509.Name(
        [
            x509.NameAttribute(NameOID.COMMON_NAME, "AC DE PRUEBA SELLADOMX"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "SelladoMX Pruebas"),
            x509.NameAttribute(NameOID.COUNTRY_NAME, "MX"),
        ]
    )
    ca_cert = (
        x509.CertificateBuilder()
        .subject_name(ca_name)
        .issuer_name(ca_name)
        .public_key(ca_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(days=1))
        .not_valid_after(now + timedelta(days=730))
        .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
        .add_extension(_key_usage(key_cert_sign=True, crl_sign=True), critical=True)
        .sign(ca_key, hashes.SHA256())
    )

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = x509.Name(
        [
            x509.NameAttribute(NameOID.COMMON_NAME, "PERSONA DE PRUEBA"),
            x509.NameAttribute(NameOID.PSEUDONYM, "PERSONA DE PRUEBA"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "PERSONA DE PRUEBA"),
            x509.NameAttribute(NameOID.COUNTRY_NAME, "MX"),
            x509.NameAttribute(NameOID.EMAIL_ADDRESS, "prueba@example.com"),
            x509.NameAttribute(NameOID.X500_UNIQUE_IDENTIFIER, "XAXX010101000"),
            x509.NameAttribute(NameOID.SERIAL_NUMBER, "XAXX010101HDFXXX01"),
        ]
    )
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(ca_name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(days=1))
        .not_valid_after(now + timedelta(days=365))
        .add_extension(
            _key_usage(digital_signature=True, content_commitment=True),
            critical=True,
        )
        .sign(ca_key, hashes.SHA256())
    )

    cert_path = directory / "prueba.cer"
    cert_path.write_bytes(cert.public_bytes(serialization.Encoding.DER))
    key_path = directory / "prueba.key"
    key_path.write_bytes(
        key.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(
                password.encode()
            ),
        )
    )
    return EFirmaFiles(cert_path, key_path, password, ca_cert)


@pytest.fixture(scope="session")
def sample_pdf(tmp_path_factory) -> Path:
    """Small valid unsigned PDF."""
    path = tmp_path_factory.mktemp("pdfs") / "sample.pdf"
    path.write_bytes(_minimal_pdf())
    return path
