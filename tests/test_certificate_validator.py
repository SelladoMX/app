"""Tests para CertificateValidator"""
import pytest
from pathlib import Path
from datetime import datetime, timedelta

from selladomx.signing.certificate_validator import CertificateValidator
from selladomx.errors import (
    CertificateError,
    CertificateExpiredError,
    CertificateValidationError
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


# Tests más completos requieren certificados de prueba reales
# que se pueden generar con OpenSSL o usar certificados e.firma de prueba del SAT
