"""SigningCoordinator - Manages SigningWorker thread and emits signals to QML."""
import logging
from pathlib import Path
from typing import List, Optional

from PySide6.QtCore import QObject, Signal

from ...signing.worker import SigningWorker
from ...signing.tsa import TSAClient

logger = logging.getLogger(__name__)


class SigningCoordinator(QObject):
    """Coordina SigningWorker (QThread) y emite signals a QML.

    This class wraps the SigningWorker to provide a clean interface
    between the QML UI and the background signing thread.
    """

    # Signals emitted to MainViewModel and QML
    progressChanged = Signal(int, int)  # current, total
    fileCompleted = Signal(str, bool, str, str)  # filename, success, message, url
    finished = Signal(list)  # List of error messages

    def __init__(self):
        """Initialize the signing coordinator."""
        super().__init__()
        self.worker: Optional[SigningWorker] = None
        self.tsa_client: Optional[TSAClient] = None

        logger.info("SigningCoordinator initialized")

    def start(
        self,
        pdf_paths: List[Path],
        cert,
        private_key,
        use_professional_tsa: bool = False,
        api_key: Optional[str] = None,
        signer_cn: str = "",
        signer_serial: str = "",
        output_dir: Optional[Path] = None,
    ):
        """Start signing process in background thread.

        Args:
            pdf_paths: List of PDF files to sign
            cert: Certificate object
            private_key: Private key object
            use_professional_tsa: Whether to use professional TSA
            api_key: API key for professional TSA
            signer_cn: Signer common name
            signer_serial: Signer serial number
            output_dir: Output directory (None = same as source)
        """
        if self.worker and self.worker.isRunning():
            logger.warning("Signing already in progress")
            return

        # Create TSA client if not using professional TSA
        if not use_professional_tsa:
            self.tsa_client = TSAClient()
        else:
            self.tsa_client = None

        # Create worker thread
        self.worker = SigningWorker(
            pdf_paths=pdf_paths,
            cert=cert,
            private_key=private_key,
            tsa_client=self.tsa_client,
            output_dir=output_dir,
            use_professional_tsa=use_professional_tsa,
            api_key=api_key,
            signer_cn=signer_cn,
            signer_serial=signer_serial,
        )

        # Connect worker signals to our signals (pass-through)
        self.worker.progress.connect(self._on_progress)
        self.worker.file_completed.connect(self._on_file_completed)
        self.worker.finished.connect(self._on_finished)

        # Start the worker thread
        self.worker.start()

        logger.info(f"Started signing {len(pdf_paths)} files")

    def _on_progress(self, current: int, total: int):
        """Handle progress signal from worker.

        Args:
            current: Current file number
            total: Total files
        """
        self.progressChanged.emit(current, total)

    def _on_file_completed(
        self, filename: str, success: bool, message: str, verification_url: str
    ):
        """Handle file completion signal from worker.

        Args:
            filename: Name of the file
            success: Whether signing was successful
            message: Status message
            verification_url: Verification URL (if professional TSA)
        """
        self.fileCompleted.emit(filename, success, message, verification_url)

    def _on_finished(self, errors: List[str]):
        """Handle finished signal from worker.

        Args:
            errors: List of error messages
        """
        self.finished.emit(errors)

        # Clean up worker
        if self.worker:
            self.worker.deleteLater()
            self.worker = None

        logger.info("Signing process finished")

    def stop(self):
        """Stop the signing process if running."""
        if self.worker and self.worker.isRunning():
            logger.info("Stopping signing process...")
            self.worker.terminate()
            self.worker.wait()
            self.worker = None
