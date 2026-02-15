"""Update checker for SelladoMX using GitHub releases API."""
import logging
from urllib.request import urlopen, Request
from urllib.error import URLError
import json

from PySide6.QtCore import QObject, Signal, Slot, QThread

logger = logging.getLogger(__name__)

GITHUB_REPO = "SelladoMX/app"
DOWNLOAD_URL = "https://www.selladomx.com/#descarga"


def _parse_version(version_str: str) -> tuple[int, ...]:
    """Parse a version string like 'v0.3.0' or '0.3.0' into a tuple of ints."""
    clean = version_str.lstrip("v")
    return tuple(int(x) for x in clean.split("."))


class _CheckWorker(QThread):
    """Background thread that fetches the latest release from GitHub."""

    result = Signal(str)  # latest version tag (e.g. "0.3.1")
    error = Signal(str)

    def run(self):
        try:
            url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
            req = Request(url, headers={"Accept": "application/vnd.github+json"})
            with urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            tag = data.get("tag_name", "")
            if tag:
                self.result.emit(tag.lstrip("v"))
            else:
                self.error.emit("No tag found in latest release")
        except (URLError, json.JSONDecodeError, OSError) as e:
            self.error.emit(str(e))


class UpdateChecker(QObject):
    """Checks for app updates against the latest GitHub release.

    Emits updateAvailable with (latest_version, download_url) if a newer
    version is found. Runs the network request in a background thread.
    """

    updateAvailable = Signal(str, str)  # latest_version, download_url

    def __init__(self, current_version: str):
        super().__init__()
        self._current_version = current_version
        self._worker = None

    @Slot()
    def check(self):
        """Start an async check for updates."""
        if self._worker and self._worker.isRunning():
            return

        self._worker = _CheckWorker(self)
        self._worker.result.connect(self._on_result)
        self._worker.error.connect(self._on_error)
        self._worker.finished.connect(self._cleanup)
        self._worker.start()

        logger.info(f"Checking for updates (current: {self._current_version})")

    def _on_result(self, latest_version: str):
        try:
            current = _parse_version(self._current_version)
            latest = _parse_version(latest_version)
        except (ValueError, AttributeError) as e:
            logger.warning(f"Failed to parse version: {e}")
            return

        if latest > current:
            logger.info(
                f"Update available: {latest_version} (current: {self._current_version})"
            )
            self.updateAvailable.emit(latest_version, DOWNLOAD_URL)
        else:
            logger.info(f"App is up to date ({self._current_version})")

    def _on_error(self, message: str):
        logger.warning(f"Update check failed: {message}")

    def _cleanup(self):
        if self._worker:
            self._worker.deleteLater()
            self._worker = None
