"""Tests para PDFSigner"""
import pytest
from pathlib import Path

from selladomx.signing.pdf_signer import PDFSigner
from selladomx.errors import PDFError, SigningError


class TestPDFSigner:
    """Tests para firma de PDFs"""

    def test_sign_nonexistent_pdf(self):
        """Test con PDF inexistente"""
        # Este test requiere un certificado válido para inicializar
        # el signer, por lo que se omite la implementación completa
        # En un entorno real, usarías fixtures con certificados de prueba
        pass

    def test_verify_unsigned_pdf(self, tmp_path):
        """Test verificando un PDF sin firma"""
        # Este test requiere un PDF válido
        # En producción, incluirías PDFs de prueba en tests/fixtures/
        pass


# Tests completos requieren:
# 1. Certificados de prueba válidos
# 2. PDFs de prueba en tests/fixtures/
# 3. Mock del TSA para no depender de servicios externos
