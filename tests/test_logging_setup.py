"""Tests for the log file setup and token redaction."""

import logging
import sys
from pathlib import Path

import pytest

from selladomx.utils import logging_setup
from selladomx.utils.logging_setup import (
    TokenRedactionFilter,
    get_log_dir,
    redact_tokens,
    setup_logging,
)


@pytest.fixture
def restore_root_logger():
    """Put the root logger back as pytest configured it."""
    root = logging.getLogger()
    handlers = list(root.handlers)
    level = root.level
    yield
    for handler in list(root.handlers):
        if handler not in handlers:
            root.removeHandler(handler)
            handler.close()
    for handler in handlers:
        if handler not in root.handlers:
            root.addHandler(handler)
    root.setLevel(level)


class TestRedaction:
    def test_masks_token_keeping_last_four(self):
        text = "selladomx://auth?token=smx_abcDEF123456XYZ9 done"
        assert redact_tokens(text) == "selladomx://auth?token=smx_…XYZ9 done"

    def test_masks_every_token(self):
        assert redact_tokens("smx_aaaa1111 and smx_bbbb2222") == (
            "smx_…1111 and smx_…2222"
        )

    def test_leaves_other_text_alone(self):
        assert redact_tokens("no tokens here") == "no tokens here"

    def test_filter_masks_args_and_exceptions(self):
        record = logging.LogRecord(
            "test", logging.ERROR, __file__, 1, "token %s", ("smx_SECRET9876",), None
        )
        try:
            raise ValueError("bad token smx_INEXC4321")
        except ValueError:
            record.exc_info = sys.exc_info()

        assert TokenRedactionFilter().filter(record) is True
        assert record.getMessage() == "token smx_…9876"
        assert "SECRET" not in record.getMessage()
        assert "smx_INEXC4321" not in record.exc_text
        assert "smx_…4321" in record.exc_text


class TestLogDir:
    def test_windows(self, monkeypatch, tmp_path):
        monkeypatch.setattr(sys, "platform", "win32")
        monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
        assert get_log_dir() == tmp_path / "SelladoMX" / "logs"

    def test_macos(self, monkeypatch):
        monkeypatch.setattr(sys, "platform", "darwin")
        assert get_log_dir() == Path.home() / "Library" / "Logs" / "SelladoMX"

    def test_linux_xdg_state_home(self, monkeypatch, tmp_path):
        monkeypatch.setattr(sys, "platform", "linux")
        monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path))
        assert get_log_dir() == tmp_path / "selladomx" / "logs"

    def test_linux_default(self, monkeypatch):
        monkeypatch.setattr(sys, "platform", "linux")
        monkeypatch.delenv("XDG_STATE_HOME", raising=False)
        assert get_log_dir() == Path.home() / ".local" / "state" / "selladomx" / "logs"


class TestSetupLogging:
    def test_writes_redacted_utf8_file(self, tmp_path, restore_root_logger):
        log_file = setup_logging(log_dir=tmp_path / "logs")

        logging.getLogger("selladomx.test").info(
            "Configurando token smx_ABCDEFGH1234 – firma válida"
        )
        for handler in logging.getLogger().handlers:
            handler.flush()

        assert log_file == tmp_path / "logs" / "selladomx.log"
        content = log_file.read_text(encoding="utf-8")
        assert "smx_ABCDEFGH1234" not in content
        assert "smx_…1234 – firma válida" in content

    def test_no_streams_and_unwritable_dir(
        self, tmp_path, monkeypatch, restore_root_logger
    ):
        monkeypatch.setattr(sys, "stdout", None)
        monkeypatch.setattr(sys, "stderr", None)
        blocker = tmp_path / "not-a-dir"
        blocker.write_text("x")

        log_file = setup_logging(log_dir=blocker / "logs")

        assert log_file is None
        logging.getLogger("selladomx.test").info("still works")

    def test_stream_handler_only_when_stream_exists(
        self, tmp_path, monkeypatch, restore_root_logger
    ):
        monkeypatch.setattr(sys, "stdout", None)
        monkeypatch.setattr(sys, "stderr", None)

        setup_logging(log_dir=tmp_path)

        handlers = logging.getLogger().handlers
        assert not any(
            type(h) is logging.StreamHandler for h in handlers
        ), "no console handler without a console"
        assert any(
            isinstance(h, logging.handlers.RotatingFileHandler) for h in handlers
        )
        assert all(
            any(isinstance(f, TokenRedactionFilter) for f in h.filters)
            for h in handlers
        )

    def test_rotation_limits(self):
        assert logging_setup.LOG_MAX_BYTES == 1_000_000
        assert logging_setup.LOG_BACKUP_COUNT == 3
