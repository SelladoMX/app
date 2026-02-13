"""Tests for MainViewModel - confirmSigning and verification URL collection."""
from unittest.mock import MagicMock, patch

import pytest

from selladomx.ui.qml_bridge.main_view_model import MainViewModel


@pytest.fixture
def view_model():
    """Create a MainViewModel with mocked dependencies."""
    settings = MagicMock()
    settings.get_last_cert_path.return_value = ""
    settings.get_last_key_path.return_value = ""
    settings.use_professional_tsa.return_value = False
    settings.get_last_credit_balance.return_value = 10
    settings.get_token.return_value = "test-token"
    settings.has_api_key.return_value = True

    coordinator = MagicMock()

    vm = MainViewModel(settings, coordinator)
    return vm


class TestConfirmSigning:
    """Tests for the confirmSigning flow."""

    def test_confirm_signing_emits_signal_when_ready(self, view_model):
        """confirmSigning should emit showConfirmSigningDialog with correct data."""
        view_model._step1_complete = True
        view_model._step2_complete = True
        view_model._pdf_files = ["/tmp/a.pdf", "/tmp/b.pdf"]
        view_model._use_professional_tsa = True
        view_model._credit_balance = 5

        signals = []
        view_model.showConfirmSigningDialog.connect(lambda *args: signals.append(args))

        view_model.confirmSigning()

        assert len(signals) == 1
        file_count, use_pro, balance = signals[0]
        assert file_count == 2
        assert use_pro is True
        assert balance == 5

    def test_confirm_signing_blocked_when_steps_incomplete(self, view_model):
        """confirmSigning should not emit when steps are incomplete."""
        view_model._step1_complete = False
        view_model._step2_complete = False

        signals = []
        view_model.showConfirmSigningDialog.connect(lambda *args: signals.append(args))

        view_model.confirmSigning()

        assert len(signals) == 0


class TestVerificationUrlCollection:
    """Tests for verification URL collection during signing."""

    def test_urls_collected_on_file_completed(self, view_model):
        """Verification URLs should be accumulated during signing."""
        view_model._verification_urls = []

        view_model._on_file_completed("doc1.pdf", True, "OK", "https://example.com/v/1")
        view_model._on_file_completed("doc2.pdf", True, "OK", "https://example.com/v/2")
        view_model._on_file_completed("doc3.pdf", True, "OK", "")

        assert len(view_model._verification_urls) == 2
        assert view_model._verification_urls[0] == {
            "filename": "doc1.pdf",
            "url": "https://example.com/v/1",
        }
        assert view_model._verification_urls[1] == {
            "filename": "doc2.pdf",
            "url": "https://example.com/v/2",
        }

    def test_urls_cleared_on_start_signing(self, view_model):
        """Verification URLs should be cleared when a new signing starts."""
        view_model._verification_urls = [{"filename": "old.pdf", "url": "https://old"}]
        view_model._step1_complete = True
        view_model._step2_complete = True
        view_model._pdf_files = ["/tmp/test.pdf"]
        view_model._use_professional_tsa = False

        view_model.startSigning()

        assert view_model._verification_urls == []

    def test_urls_emitted_on_signing_finished(self, view_model):
        """verificationUrlsReady should be emitted when signing finishes with URLs."""
        view_model._verification_urls = [
            {"filename": "a.pdf", "url": "https://example.com/v/a"},
        ]
        view_model._pdf_files = ["/tmp/a.pdf"]
        view_model._use_professional_tsa = True
        view_model._is_signing = True

        emitted = []
        view_model.verificationUrlsReady.connect(lambda urls: emitted.append(urls))

        view_model._on_signing_finished([])

        assert len(emitted) == 1
        assert emitted[0][0]["filename"] == "a.pdf"

    def test_urls_not_emitted_when_empty(self, view_model):
        """verificationUrlsReady should NOT be emitted when no URLs collected."""
        view_model._verification_urls = []
        view_model._pdf_files = ["/tmp/a.pdf"]
        view_model._is_signing = True

        emitted = []
        view_model.verificationUrlsReady.connect(lambda urls: emitted.append(urls))

        view_model._on_signing_finished([])

        assert len(emitted) == 0


class TestTokenConfiguredViaDeepLink:
    """Tests for the deep link token notification signal."""

    def test_signal_exists(self, view_model):
        """tokenConfiguredViaDeepLink signal should exist on MainViewModel."""
        # Just verify the signal can be connected
        emitted = []
        view_model.tokenConfiguredViaDeepLink.connect(lambda: emitted.append(True))
        view_model.tokenConfiguredViaDeepLink.emit()
        assert len(emitted) == 1
