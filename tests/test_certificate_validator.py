"""Tests para CertificateValidator"""

import logging
from datetime import UTC, datetime, timedelta

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from selladomx.signing.certificate_validator import CertificateValidator
from selladomx.errors import (
    CertificateError,
    CertificateKeyMismatchError,
    CertificatePasswordError,
)


class TestCertificateValidator:
    """Tests para validación de certificados"""

    def test_missing_certificate_file(self, tmp_path):
        """Test con archivo de certificado inexistente"""
        cert_path = tmp_path / "nonexistent.cer"
        key_path = tmp_path / "test.key"
        key_path.touch()

        validator = CertificateValidator(cert_path, key_path, "password")

        with pytest.raises(CertificateError, match="no encontrado"):
            validator.validate_all()

    def test_missing_key_file(self, tmp_path):
        """Test con archivo de clave inexistente"""
        cert_path = tmp_path / "test.cer"
        cert_path.touch()
        key_path = tmp_path / "nonexistent.key"

        validator = CertificateValidator(cert_path, key_path, "password")

        with pytest.raises(CertificateError):
            validator.validate_all()

    def test_invalid_certificate_format(self, tmp_path):
        """Test con certificado en formato inválido"""
        cert_path = tmp_path / "invalid.cer"
        cert_path.write_bytes(b"not a valid certificate")
        key_path = tmp_path / "test.key"
        key_path.touch()

        validator = CertificateValidator(cert_path, key_path, "password")

        with pytest.raises(CertificateError, match="No se pudo cargar"):
            validator.validate_all()


def _write_efirma(directory, password="Prueba1234", key=None, cert_key=None):
    """Write a SAT-style DER .cer and encrypted PKCS#8 DER .key."""
    key = key or rsa.generate_private_key(public_exponent=65537, key_size=2048)
    cert_key = cert_key or key
    name = x509.Name(
        [
            x509.NameAttribute(NameOID.COMMON_NAME, "PERSONA DE PRUEBA"),
            x509.NameAttribute(NameOID.SERIAL_NUMBER, "XAXX010101HDFXXX01"),
        ]
    )
    now = datetime.now(UTC)
    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(cert_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(days=1))
        .not_valid_after(now + timedelta(days=30))
        .sign(cert_key, hashes.SHA256())
    )
    cert_path = directory / "prueba.cer"
    cert_path.write_bytes(cert.public_bytes(serialization.Encoding.DER))
    key_path = directory / "prueba.key"
    encryption = (
        serialization.BestAvailableEncryption(password.encode())
        if password
        else serialization.NoEncryption()
    )
    key_path.write_bytes(
        key.private_bytes(
            serialization.Encoding.DER, serialization.PrivateFormat.PKCS8, encryption
        )
    )
    return cert_path, key_path


class TestKeyLoading:
    def test_valid_efirma(self, tmp_path):
        cert_path, key_path = _write_efirma(tmp_path)
        cert, key = CertificateValidator(
            cert_path, key_path, "Prueba1234"
        ).validate_all()
        assert cert.public_key().public_numbers() == key.public_key().public_numbers()

    def test_wrong_password(self, tmp_path):
        cert_path, key_path = _write_efirma(tmp_path)
        validator = CertificateValidator(cert_path, key_path, "otra")
        with pytest.raises(CertificatePasswordError, match="Contraseña incorrecta"):
            validator.validate_all()

    def test_missing_password(self, tmp_path):
        cert_path, key_path = _write_efirma(tmp_path)
        with pytest.raises(CertificatePasswordError, match="contraseña"):
            CertificateValidator(cert_path, key_path, "").validate_all()

    def test_unencrypted_key_with_password_typed(self, tmp_path):
        cert_path, key_path = _write_efirma(tmp_path, password="")
        CertificateValidator(cert_path, key_path, "lo-que-sea").validate_all()

    def test_unrecognized_key_format(self, tmp_path):
        cert_path, key_path = _write_efirma(tmp_path)
        key_path.write_bytes(b"esto no es una clave")
        with pytest.raises(CertificateError) as exc_info:
            CertificateValidator(cert_path, key_path, "Prueba1234").validate_all()
        assert not isinstance(exc_info.value, CertificatePasswordError)
        assert "formato" in str(exc_info.value)

    def test_key_from_another_efirma(self, tmp_path):
        other = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        cert_path, key_path = _write_efirma(tmp_path, cert_key=other)
        with pytest.raises(CertificateKeyMismatchError, match="no corresponde"):
            CertificateValidator(cert_path, key_path, "Prueba1234").validate_all()

    def test_logs_cn_but_not_full_subject(self, tmp_path, caplog):
        cert_path, key_path = _write_efirma(tmp_path)
        with caplog.at_level(logging.DEBUG, logger="selladomx"):
            CertificateValidator(cert_path, key_path, "Prueba1234").validate_all()
        assert "PERSONA DE PRUEBA" in caplog.text
        assert "XAXX010101HDFXXX01" not in caplog.text
