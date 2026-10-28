"""Tests for MainViewModel - confirmSigning and verification URL collection."""

from unittest.mock import MagicMock, patch

import pytest

from selladomx.config import API_BASE_URL
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

        url1 = f"{API_BASE_URL}/verify/1"
        url2 = f"{API_BASE_URL}/verify/2"
        view_model._on_file_completed("doc1.pdf", True, "OK", url1)
        view_model._on_file_completed("doc2.pdf", True, "OK", url2)
        view_model._on_file_completed("doc3.pdf", True, "OK", "")

        assert len(view_model._verification_urls) == 2
        assert view_model._verification_urls[0] == {
            "filename": "doc1.pdf",
            "url": url1,
        }
        assert view_model._verification_urls[1] == {
            "filename": "doc2.pdf",
            "url": url2,
        }

    def test_urls_outside_api_host_are_dropped(self, view_model):
        """Server-supplied URLs on another host must not reach the dialog."""
        view_model._verification_urls = []

        view_model._on_file_completed("a.pdf", True, "OK", "https://evil.example/v/1")
        view_model._on_file_completed("b.pdf", True, "OK", "javascript:alert(1)")

        assert view_model._verification_urls == []

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
        emitted = []
        view_model.tokenConfiguredViaDeepLink.connect(lambda: emitted.append(True))
        view_model.tokenConfiguredViaDeepLink.emit()
        assert len(emitted) == 1


class TestFailedFiles:
    """Tests for the per-file errors shown in the result dialog."""

    def test_failed_files_emitted_on_finish(self, view_model):
        view_model._pdf_files = ["/tmp/a.pdf", "/tmp/b.pdf"]
        view_model._is_signing = True
        view_model._on_file_completed("a.pdf", True, "OK", "")
        view_model._on_file_completed("b.pdf", False, "Sin conexión", "")

        emitted = []
        view_model.failedFilesReady.connect(lambda failed: emitted.append(failed))
        view_model._on_signing_finished(["b.pdf: Sin conexión"])

        assert emitted == [[{"filename": "b.pdf", "message": "Sin conexión"}]]


class TestStatusLog:
    """Tests for the HTML status log."""

    def test_dynamic_text_is_escaped(self, view_model):
        view_model._status_log = ""
        view_model._append_status_log('<img src="x"> & <b>', "#000000")

        assert "<img" not in view_model._status_log
        assert "&lt;img src=&quot;x&quot;&gt; &amp; &lt;b&gt;" in view_model._status_log

    def test_newlines_become_line_breaks(self, view_model):
        view_model._status_log = ""
        view_model._append_status_log("uno\ndos", "#000000")

        assert "uno<br>dos" in view_model._status_log


class TestDeepLinkTokenConfirmation:
    """A deep link token is saved only after the user confirms it."""

    BALANCE = {
        "credits_remaining": 42,
        "email": "ana@example.com",
        "plan": "individual",
        "token_info": {
            "is_primary": False,
            "alias": "Oficina",
            "expires_at": "2027-01-01T00:00:00Z",
            "is_active": True,
        },
    }

    def _request(self, view_model, token="smx_NEWTOKEN1234"):
        requested = []
        view_model.deepLinkTokenConfirmationRequested.connect(
            lambda info: requested.append(info)
        )
        with patch("selladomx.api.client.SelladoMXAPIClient") as client_cls:
            client_cls.return_value.get_balance.return_value = dict(self.BALANCE)
            view_model.handleDeepLinkToken(token)
        return requested

    def test_request_does_not_save(self, view_model):
        requested = self._request(view_model)

        view_model.settings.set_token.assert_not_called()
        assert requested == [
            {
                "email": "ana@example.com",
                "credits_remaining": 42,
                "is_primary": False,
                "alias": "Oficina",
                "expires_at": "2027-01-01T00:00:00Z",
                "replaces_existing": True,
            }
        ]

    def test_confirm_saves_token(self, view_model):
        configured = []
        view_model.tokenConfiguredViaDeepLink.connect(lambda: configured.append(True))
        self._request(view_model)

        view_model.confirmDeepLinkToken()

        view_model.settings.set_token.assert_called_once_with("smx_NEWTOKEN1234")
        view_model.settings.set_token_info.assert_called_once()
        view_model.settings.set_last_credit_balance.assert_called_with(42)
        assert view_model.creditBalance == 42
        assert configured == [True]

    def test_cancel_saves_nothing(self, view_model):
        self._request(view_model)

        view_model.cancelDeepLinkToken()
        view_model.confirmDeepLinkToken()

        view_model.settings.set_token.assert_not_called()
        view_model.settings.set_token_info.assert_not_called()

    def test_api_error_saves_nothing(self, view_model):
        from selladomx.api.exceptions import AuthenticationError

        requested = []
        view_model.deepLinkTokenConfirmationRequested.connect(
            lambda info: requested.append(info)
        )
        with patch("selladomx.api.client.SelladoMXAPIClient") as client_cls:
            client_cls.return_value.get_balance.side_effect = AuthenticationError(
                "Invalid API key"
            )
            view_model.handleDeepLinkToken("smx_BADTOKEN0000")
        view_model.confirmDeepLinkToken()

        assert requested == []
        view_model.settings.set_token.assert_not_called()

    def test_same_token_skips_dialog(self, view_model):
        view_model.settings.get_token.return_value = "smx_SAMETOKEN999"
        with patch.object(view_model, "_refresh_credit_balance"):
            requested = self._request(view_model, token="smx_SAMETOKEN999")

        assert requested == []
        view_model.settings.set_token.assert_not_called()

    def test_no_existing_token_is_reported(self, view_model):
        view_model.settings.get_token.return_value = None
        requested = self._request(view_model)

        assert requested[0]["replaces_existing"] is False

    def test_dead_url_slot_removed(self, view_model):
        assert not hasattr(view_model, "handleDeepLink")


class TestOpenTrustedUrl:
    """Server-supplied URLs are opened only on the API host."""

    def test_refuses_other_hosts(self, view_model):
        with patch("selladomx.ui.qml_bridge.main_view_model.QDesktopServices") as qds:
            assert view_model.openTrustedUrl("https://evil.example/verify/1") is False
            qds.openUrl.assert_not_called()

    def test_opens_api_host(self, view_model):
        with patch("selladomx.ui.qml_bridge.main_view_model.QDesktopServices") as qds:
            qds.openUrl.return_value = True
            assert view_model.openTrustedUrl(f"{API_BASE_URL}/verify/1") is True
            qds.openUrl.assert_called_once()

    def test_verification_page_escapes_token(self, view_model):
        with patch("selladomx.ui.qml_bridge.main_view_model.QDesktopServices") as qds:
            qds.openUrl.return_value = True
            view_model.openVerificationPage("abc'/../x?y")
            opened = qds.openUrl.call_args[0][0].toEncoded().data().decode()

        assert opened.startswith(f"{API_BASE_URL}/verify/")
        assert "'" not in opened and "?" not in opened
