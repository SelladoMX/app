"""Tests para PDFSigner"""
import pytest
from pathlib import Path

from selladomx.signing.pdf_signer import PDFSigner
from selladomx.errors import PDFError, SigningError


class TestPDFSigner:
    """Tests para firma de PDFs"""

    def test_sign_nonexistent_pdf(self):
        """Test con PDF inexistente"""
        # Sin implementar: inicializar el signer requiere un certificado válido
        pass

    def test_verify_unsigned_pdf(self, tmp_path):
        """Test verificando un PDF sin firma"""
        # Sin implementar: requiere un PDF válido
        pass
