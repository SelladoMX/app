"""Tests for SELLADOMX_API_URL validation and server-URL checks."""

import pytest

from selladomx.config import DEFAULT_API_BASE_URL, resolve_api_base_url
from selladomx.utils.urls import is_trusted_api_url, verification_page_url


class TestResolveApiBaseUrl:
    @pytest.mark.parametrize("value", [None, ""])
    def test_unset_uses_default(self, value):
        assert resolve_api_base_url(value) == DEFAULT_API_BASE_URL

    @pytest.mark.parametrize(
        "value, expected",
        [
            ("https://staging.selladomx.com", "https://staging.selladomx.com"),
            ("https://staging.selladomx.com/", "https://staging.selladomx.com"),
            ("http://localhost:8787", "http://localhost:8787"),
            ("http://127.0.0.1:8787", "http://127.0.0.1:8787"),
        ],
    )
    def test_accepted(self, value, expected):
        assert resolve_api_base_url(value) == expected

    @pytest.mark.parametrize(
        "value",
        [
            "http://evil.example.com",
            "http://localhost.evil.example.com",
            "ftp://www.selladomx.com",
            "www.selladomx.com",
            "https://",
            "javascript:alert(1)",
        ],
    )
    def test_rejected_falls_back_to_default(self, value, caplog):
        assert resolve_api_base_url(value) == DEFAULT_API_BASE_URL
        assert "Ignoring SELLADOMX_API_URL" in caplog.text


class TestTrustedApiUrl:
    BASE = "https://www.selladomx.com"

    @pytest.mark.parametrize(
        "url",
        [
            "https://www.selladomx.com/verify/abc",
            "https://WWW.SELLADOMX.COM/verify/abc",
        ],
    )
    def test_accepts_api_host(self, url):
        assert is_trusted_api_url(url, self.BASE)

    @pytest.mark.parametrize(
        "url",
        [
            "http://www.selladomx.com/verify/abc",
            "https://evil.example/verify/abc",
            "https://www.selladomx.com.evil.example/verify",
            "https://www.selladomx.com@evil.example/verify",
            "https://user@www.selladomx.com/verify",
            "https://www.selladomx.com:8443/verify",
            "javascript:alert(1)",
            "file:///etc/passwd",
            "",
        ],
    )
    def test_rejects_everything_else(self, url):
        assert not is_trusted_api_url(url, self.BASE)

    def test_local_dev_server_allows_http(self):
        base = "http://localhost:8787"
        assert is_trusted_api_url("http://localhost:8787/verify/x", base)
        assert not is_trusted_api_url("http://localhost:9999/verify/x", base)

    def test_verification_page_url_quotes_token(self):
        url = verification_page_url("a'b/<c>", self.BASE)
        assert url == "https://www.selladomx.com/verify/a%27b%2F%3Cc%3E"
        assert is_trusted_api_url(url, self.BASE)

    def test_verification_page_url_empty(self):
        assert verification_page_url("", self.BASE) == ""
