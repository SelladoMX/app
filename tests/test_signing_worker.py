"""Tests for SigningWorker error handling - no silent fallback to free TSA."""
import hashlib
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock

import pytest

from selladomx.signing.worker import SigningWorker
from selladomx.api.exceptions import (
    AuthenticationError,
    InsufficientCreditsError,
    NetworkError,
    APIError,
)


@pytest.fixture
def mock_signer():
    """Create a mock PDFSigner."""
    with patch("selladomx.signing.worker.PDFSigner") as mock_cls:
        signer = mock_cls.return_value
        output_path = Path("/tmp/test_firmado.pdf")
        signer.sign_pdf.return_value = output_path

        # Mock output_path.read_bytes() and stat()
        with patch.object(Path, "read_bytes", return_value=b"signed-pdf-content"):
            with patch.object(Path, "stat") as mock_stat:
                mock_stat.return_value = MagicMock(st_size=1024)
                yield signer


class TestSigningWorkerNoFallback:
    """Test that professional TSA errors stop signing instead of falling back."""

    def _create_worker(self, use_professional=True, api_key="test-key"):
        worker = SigningWorker(
            pdf_paths=[Path("/tmp/test.pdf")],
            cert=MagicMock(),
            private_key=MagicMock(),
            use_professional_tsa=use_professional,
            api_key=api_key,
            signer_cn="Test User",
            signer_serial="12345",
        )
        return worker

    @patch("selladomx.signing.worker.SelladoMXAPIClient")
    @patch("selladomx.signing.worker.PDFSigner")
    def test_insufficient_credits_emits_error_no_fallback(self, mock_signer_cls, mock_api_cls):
        """InsufficientCreditsError should emit failure, not silently sign with free TSA."""
        mock_api = mock_api_cls.return_value
        mock_api.request_tsa_sign.side_effect = InsufficientCreditsError()

        # sign_pdf raises InsufficientCreditsError because APITimeStamper
        # calls request_tsa_sign during signing
        mock_signer = mock_signer_cls.return_value
        mock_signer.sign_pdf.side_effect = InsufficientCreditsError()

        worker = self._create_worker()

        # Collect emitted signals
        completed_calls = []
        worker.file_completed.connect(lambda *args: completed_calls.append(args))

        finished_errors = []
        worker.finished.connect(lambda errs: finished_errors.extend(errs))

        with patch.object(Path, "read_bytes", return_value=b"content"):
            with patch.object(Path, "stat", return_value=MagicMock(st_size=100)):
                worker.run()

        # Should have emitted file_completed with success=False
        assert len(completed_calls) == 1
        filename, success, message, url = completed_calls[0]
        assert success is False
        assert "créditos" in message.lower()
        assert url == ""

        # Should have errors
        assert len(finished_errors) == 1

    @patch("selladomx.signing.worker.SelladoMXAPIClient")
    @patch("selladomx.signing.worker.PDFSigner")
    def test_auth_error_emits_error_no_fallback(self, mock_signer_cls, mock_api_cls):
        """AuthenticationError should emit failure, not silently sign with free TSA."""
        mock_signer = mock_signer_cls.return_value
        mock_signer.sign_pdf.side_effect = AuthenticationError("Invalid token")

        worker = self._create_worker()

        completed_calls = []
        worker.file_completed.connect(lambda *args: completed_calls.append(args))

        finished_errors = []
        worker.finished.connect(lambda errs: finished_errors.extend(errs))

        with patch.object(Path, "read_bytes", return_value=b"content"):
            with patch.object(Path, "stat", return_value=MagicMock(st_size=100)):
                worker.run()

        assert len(completed_calls) == 1
        _, success, message, _ = completed_calls[0]
        assert success is False
        assert "token" in message.lower()

    @patch("selladomx.signing.worker.SelladoMXAPIClient")
    @patch("selladomx.signing.worker.PDFSigner")
    def test_network_error_emits_error_no_fallback(self, mock_signer_cls, mock_api_cls):
        """NetworkError should emit failure, not silently sign with free TSA."""
        mock_signer = mock_signer_cls.return_value
        mock_signer.sign_pdf.side_effect = NetworkError("Connection refused")

        worker = self._create_worker()

        completed_calls = []
        worker.file_completed.connect(lambda *args: completed_calls.append(args))

        finished_errors = []
        worker.finished.connect(lambda errs: finished_errors.extend(errs))

        with patch.object(Path, "read_bytes", return_value=b"content"):
            with patch.object(Path, "stat", return_value=MagicMock(st_size=100)):
                worker.run()

        assert len(completed_calls) == 1
        _, success, message, _ = completed_calls[0]
        assert success is False
        assert "connection refused" in message.lower()

    @patch("selladomx.signing.worker.SelladoMXAPIClient")
    @patch("selladomx.signing.worker.PDFSigner")
    def test_api_error_emits_error_no_fallback(self, mock_signer_cls, mock_api_cls):
        """Generic APIError should emit failure, not silently sign with free TSA."""
        mock_signer = mock_signer_cls.return_value
        mock_signer.sign_pdf.side_effect = APIError("Server error", 500)

        worker = self._create_worker()

        completed_calls = []
        worker.file_completed.connect(lambda *args: completed_calls.append(args))

        finished_errors = []
        worker.finished.connect(lambda errs: finished_errors.extend(errs))

        with patch.object(Path, "read_bytes", return_value=b"content"):
            with patch.object(Path, "stat", return_value=MagicMock(st_size=100)):
                worker.run()

        assert len(completed_calls) == 1
        _, success, message, _ = completed_calls[0]
        assert success is False

    @patch("selladomx.signing.worker.APITimeStamper")
    @patch("selladomx.signing.worker.SelladoMXAPIClient")
    @patch("selladomx.signing.worker.PDFSigner")
    def test_professional_tsa_success_emits_verification_url(
        self, mock_signer_cls, mock_api_cls, mock_timestamper_cls
    ):
        """Successful professional TSA should emit verification URL."""
        mock_signer = mock_signer_cls.return_value
        output_path = Path("/tmp/test_firmado.pdf")
        mock_signer.sign_pdf.return_value = output_path

        mock_api = mock_api_cls.return_value
        mock_api.complete_timestamp.return_value = {"success": True}

        # Set up the APITimeStamper mock to have record_id and verification_url
        # (these get set during signing via async_request_tsa_response)
        mock_timestamper = mock_timestamper_cls.return_value
        mock_timestamper.record_id = "test-record-id"
        mock_timestamper.verification_url = "https://selladomx.com/verify/abc123"

        worker = self._create_worker()

        completed_calls = []
        worker.file_completed.connect(lambda *args: completed_calls.append(args))

        with patch.object(Path, "read_bytes", return_value=b"content"):
            with patch.object(Path, "stat", return_value=MagicMock(st_size=100)):
                worker.run()

        assert len(completed_calls) == 1
        _, success, _, url = completed_calls[0]
        assert success is True
        assert url == "https://selladomx.com/verify/abc123"

    @patch("selladomx.signing.worker.SelladoMXAPIClient")
    @patch("selladomx.signing.worker.PDFSigner")
    def test_multiple_files_stops_on_first_tsa_error(self, mock_signer_cls, mock_api_cls):
        """When TSA fails, should stop processing remaining files."""
        mock_signer = mock_signer_cls.return_value
        mock_signer.sign_pdf.side_effect = InsufficientCreditsError()

        worker = SigningWorker(
            pdf_paths=[Path("/tmp/a.pdf"), Path("/tmp/b.pdf"), Path("/tmp/c.pdf")],
            cert=MagicMock(),
            private_key=MagicMock(),
            use_professional_tsa=True,
            api_key="test-key",
            signer_cn="Test",
            signer_serial="123",
        )

        completed_calls = []
        worker.file_completed.connect(lambda *args: completed_calls.append(args))

        with patch.object(Path, "read_bytes", return_value=b"content"):
            with patch.object(Path, "stat", return_value=MagicMock(st_size=100)):
                worker.run()

        # Should only have processed the first file, then stopped
        assert len(completed_calls) == 1

    @patch("selladomx.signing.worker.PDFSigner")
    def test_free_tsa_signing_works_without_api(self, mock_signer_cls):
        """Free TSA signing should work without API client."""
        mock_signer = mock_signer_cls.return_value
        output_path = Path("/tmp/test_firmado.pdf")
        mock_signer.sign_pdf.return_value = output_path

        worker = SigningWorker(
            pdf_paths=[Path("/tmp/test.pdf")],
            cert=MagicMock(),
            private_key=MagicMock(),
            use_professional_tsa=False,
        )

        completed_calls = []
        worker.file_completed.connect(lambda *args: completed_calls.append(args))

        worker.run()

        assert len(completed_calls) == 1
        _, success, _, url = completed_calls[0]
        assert success is True
        assert url == ""
