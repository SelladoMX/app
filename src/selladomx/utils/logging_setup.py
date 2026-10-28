"""Logging configuration: rotating log file, console output and token redaction.

This module must not import ``selladomx.config``: logging is configured before
config is imported so that config's import-time log lines reach the log file.
"""

import logging
import logging.handlers
import os
import platform
import re
import sys
from pathlib import Path
from typing import Optional

LOG_FILE_NAME = "selladomx.log"
LOG_MAX_BYTES = 1_000_000
LOG_BACKUP_COUNT = 3
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

_TOKEN_PATTERN = re.compile(r"smx_[A-Za-z0-9]+")

logger = logging.getLogger(__name__)


def redact_tokens(text: str) -> str:
    """Mask SelladoMX API tokens, keeping only the last four characters.

    Args:
        text: Text that may contain tokens

    Returns:
        Text with every ``smx_...`` token replaced by ``smx_…<last4>``
    """
    return _TOKEN_PATTERN.sub(lambda m: "smx_…" + m.group(0)[-4:], text)


class TokenRedactionFilter(logging.Filter):
    """Handler filter that masks API tokens in messages and tracebacks.

    Attach it to handlers, not loggers: logger filters don't run for records
    propagated from child loggers.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            message = record.getMessage()
        except Exception:
            message = str(record.msg)
        record.msg = redact_tokens(message)
        record.args = None
        if record.exc_info and not record.exc_text:
            record.exc_text = logging.Formatter().formatException(record.exc_info)
        if record.exc_text:
            record.exc_text = redact_tokens(record.exc_text)
        if record.stack_info:
            record.stack_info = redact_tokens(record.stack_info)
        return True


def get_log_dir() -> Path:
    """Return the per-user log directory for the current OS.

    Returns:
        Windows: ``%LOCALAPPDATA%\\SelladoMX\\logs``;
        macOS: ``~/Library/Logs/SelladoMX``;
        Linux and others: ``$XDG_STATE_HOME/selladomx/logs``
        (``~/.local/state`` by default; Flatpak sets ``XDG_STATE_HOME`` to the
        app's sandbox directory).
    """
    home = Path.home()
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA")
        base_path = Path(base) if base else home / "AppData" / "Local"
        return base_path / "SelladoMX" / "logs"
    if sys.platform == "darwin":
        return home / "Library" / "Logs" / "SelladoMX"
    state_home = os.environ.get("XDG_STATE_HOME")
    base_path = Path(state_home) if state_home else home / ".local" / "state"
    return base_path / "selladomx" / "logs"


def setup_logging(
    level: int = logging.INFO, log_dir: Optional[Path] = None
) -> Optional[Path]:
    """Configure the root logger with a rotating file and, if available, a console.

    Never raises: if the log directory can't be created the app still starts,
    logging only to the console (if any).

    Args:
        level: Root logger level
        log_dir: Directory for the log file (defaults to ``get_log_dir()``)

    Returns:
        Path of the log file, or None if file logging couldn't be set up
    """
    root = logging.getLogger()
    for handler in list(root.handlers):
        root.removeHandler(handler)
        handler.close()
    root.setLevel(level)

    formatter = logging.Formatter(LOG_FORMAT)
    redaction = TokenRedactionFilter()

    # sys.stdout and sys.stderr are None in windowed PyInstaller builds.
    stream = sys.stdout or sys.stderr
    if stream is not None:
        stream_handler = logging.StreamHandler(stream)
        stream_handler.setFormatter(formatter)
        stream_handler.addFilter(redaction)
        root.addHandler(stream_handler)

    log_file: Optional[Path] = None
    file_error: Optional[Exception] = None
    try:
        target_dir = log_dir if log_dir is not None else get_log_dir()
        target_dir.mkdir(parents=True, exist_ok=True)
        log_file = target_dir / LOG_FILE_NAME
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=LOG_MAX_BYTES,
            backupCount=LOG_BACKUP_COUNT,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        file_handler.addFilter(redaction)
        root.addHandler(file_handler)
    except Exception as e:
        log_file = None
        file_error = e

    if not root.handlers:
        root.addHandler(logging.NullHandler())

    if file_error is not None:
        logger.warning(f"File logging disabled: {file_error}")

    return log_file


def log_startup_info(app_version: str, log_file: Optional[Path]) -> None:
    """Log app, OS, Python and Qt versions to help diagnose user reports.

    Args:
        app_version: SelladoMX version string
        log_file: Path of the active log file, if any
    """
    from PySide6 import __version__ as pyside_version
    from PySide6.QtCore import qVersion

    logger.info(f"SelladoMX {app_version}")
    logger.info(
        f"OS: {platform.system()} {platform.release()} ({platform.platform()}), "
        f"arch {platform.machine()}"
    )
    logger.info(
        f"Python {platform.python_version()}, Qt {qVersion()}, "
        f"PySide6 {pyside_version}, frozen={getattr(sys, 'frozen', False)}"
    )
    if os.environ.get("FLATPAK_ID"):
        logger.info(f"Running inside Flatpak ({os.environ['FLATPAK_ID']})")
    if log_file is not None:
        logger.info(f"Log file: {log_file}")


def install_qt_message_handler() -> None:
    """Route Qt and QML warnings (e.g. QML ReferenceErrors) into Python logging."""
    from PySide6.QtCore import QtMsgType, qInstallMessageHandler

    qt_logger = logging.getLogger("qt")
    levels = {
        QtMsgType.QtDebugMsg: logging.DEBUG,
        QtMsgType.QtInfoMsg: logging.INFO,
        QtMsgType.QtWarningMsg: logging.WARNING,
        QtMsgType.QtCriticalMsg: logging.ERROR,
        QtMsgType.QtFatalMsg: logging.CRITICAL,
    }

    def handler(msg_type, context, message):
        location = ""
        if context is not None and context.file:
            location = f" ({context.file}:{context.line})"
        qt_logger.log(levels.get(msg_type, logging.INFO), f"{message}{location}")

    qInstallMessageHandler(handler)


def install_excepthook() -> None:
    """Log uncaught exceptions, including those raised in Qt slots.

    Windowed builds have no stderr, so without this tracebacks are lost.
    """
    previous_hook = sys.excepthook

    def hook(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            previous_hook(exc_type, exc_value, exc_traceback)
            return
        logging.getLogger("selladomx").critical(
            "Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback)
        )

    sys.excepthook = hook
