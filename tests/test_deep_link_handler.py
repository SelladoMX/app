"""Tests for deep link parsing and the log-safe description of deep links."""

import logging
import sys

import pytest

from selladomx.utils.deep_link_handler import DeepLinkHandler, describe_deep_link
from selladomx.utils.platform_helpers import (
    quote_desktop_exec_arg,
    register_url_scheme_linux,
)

TOKEN = "smx_" + "a1B2" * 8


class TestDescribeDeepLink:
    def test_drops_query(self):
        url = f"selladomx://auth?token={TOKEN}"
        assert describe_deep_link(url) == "selladomx://auth"

    def test_invalid(self):
        assert describe_deep_link("not a url") == "<invalid>"


class TestDeepLinkHandler:
    @pytest.fixture
    def handler(self, monkeypatch):
        from selladomx.api.client import SelladoMXAPIClient

        monkeypatch.setattr(
            SelladoMXAPIClient,
            "validate_token_format",
            staticmethod(lambda token: token.startswith("smx_")),
        )
        return DeepLinkHandler()

    def test_emits_token(self, handler):
        received = []
        handler.token_received.connect(received.append)
        handler.handle_url(f"selladomx://auth?token={TOKEN}")
        assert received == [TOKEN]

    @pytest.mark.parametrize(
        "url",
        [
            f"https://auth?token={TOKEN}",
            f"selladomx://other?token={TOKEN}",
            "selladomx://auth",
            "selladomx://auth?token=bad",
        ],
    )
    def test_rejects_invalid(self, handler, url):
        received = []
        handler.token_received.connect(received.append)
        handler.handle_url(url)
        assert received == []

    @pytest.mark.parametrize(
        "url",
        [
            f"selladomx://auth?token={TOKEN}",
            f"selladomx://{TOKEN}?token={TOKEN}",
            f"selladomx://auth?token={TOKEN}x!",
        ],
    )
    def test_never_logs_token(self, handler, url, caplog):
        with caplog.at_level(logging.DEBUG):
            handler.handle_url(url)
        assert TOKEN not in caplog.text


class TestLinuxDesktopFile:
    def test_plain_path_unquoted(self):
        assert quote_desktop_exec_arg("/usr/bin/selladomx") == "/usr/bin/selladomx"

    def test_path_with_spaces_quoted(self):
        assert (
            quote_desktop_exec_arg("/home/ana/Mis Apps/SelladoMX")
            == '"/home/ana/Mis Apps/SelladoMX"'
        )

    def test_reserved_characters_escaped(self):
        # Spec: `"`, `$`, backtick and backslash are backslash-escaped inside
        # quotes, then every backslash is doubled by the string escaping.
        assert quote_desktop_exec_arg('/a b/$x"`\\') == (
            '"/a b/\\\\$x\\\\"\\\\`\\\\\\\\"'
        )

    def test_percent_escaped(self):
        assert quote_desktop_exec_arg("/opt/100%/app") == "/opt/100%%/app"

    def test_skipped_inside_flatpak(self, monkeypatch, tmp_path):
        monkeypatch.setattr(sys, "platform", "linux")
        monkeypatch.setenv("FLATPAK_ID", "com.selladomx.SelladoMX")
        monkeypatch.setenv("HOME", str(tmp_path))

        assert register_url_scheme_linux() is True
        assert not (tmp_path / ".local" / "share" / "applications").exists()
