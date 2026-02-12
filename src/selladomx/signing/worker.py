"""Background worker for PDF signing operations."""
import hashlib
import logging
from pathlib import Path
from typing import List, Optional

from PySide6.QtCore import QThread, Signal

from ..api.client import SelladoMXAPIClient
from ..api.exceptions import InsufficientCreditsError, NetworkError, APIError
from ..config import SIGNED_SUFFIX
from .pdf_signer import PDFSigner
from .tsa import TSAClient


logger = logging.getLogger(__name__)


class SigningWorker(QThread):
    """Worker thread for signing PDFs in the background.

    Emits signals for progress updates and completion.
    """

    progress = Signal(int, int)  # current, total
    file_completed = Signal(
        str, bool, str, str
    )  # filename, success, message, verification_url
    finished = Signal(list)  # List of error messages

    def __init__(
        self,
        pdf_paths: List[Path],
        cert,
        private_key,
        tsa_client: Optional[TSAClient] = None,
        output_dir: Optional[Path] = None,
        use_professional_tsa: bool = False,
        api_key: Optional[str] = None,
        signer_cn: str = "",
        signer_serial: str = "",
    ):
        """Initialize signing worker.

        Args:
            pdf_paths: List of PDF files to sign
            cert: Certificate object
            private_key: Private key object
            tsa_client: TSA client instance
            output_dir: Output directory (None = same as source)
            use_professional_tsa: Whether to use professional TSA
            api_key: API key for professional TSA
            signer_cn: Signer common name
            signer_serial: Signer serial number
        """
        super().__init__()
        self.pdf_paths = pdf_paths
        self.cert = cert
        self.private_key = private_key
        self.tsa_client = tsa_client
        self.output_dir = output_dir
        self.use_professional_tsa = use_professional_tsa
        self.api_key = api_key
        self.signer_cn = signer_cn
        self.signer_serial = signer_serial
        self.errors = []

    def run(self):
        """Execute signing process."""
        signer = PDFSigner(self.cert, self.private_key, self.tsa_client)
        total = len(self.pdf_paths)

        api_client = None
        if self.use_professional_tsa and self.api_key:
            api_client = SelladoMXAPIClient(api_key=self.api_key)

        for i, pdf_path in enumerate(self.pdf_paths, 1):
            self.progress.emit(i, total)

            try:
                # Calculate output_path if output directory was specified
                if self.output_dir:
                    output_path = (
                        self.output_dir
                        / f"{pdf_path.stem}{SIGNED_SUFFIX}{pdf_path.suffix}"
                    )
                else:
                    output_path = None  # Use default (same folder as source)

                output_path = signer.sign_pdf(pdf_path, output_path)

                # Professional TSA registration
                verification_url = ""
                if api_client and self.use_professional_tsa:
                    try:
                        file_hash = hashlib.sha256(output_path.read_bytes()).hexdigest()
                        file_size = output_path.stat().st_size
                        response = api_client.request_timestamp(
                            document_hash=file_hash,
                            filename=pdf_path.name,
                            size_bytes=file_size,
                            signer_cn=self.signer_cn,
                            signer_serial=self.signer_serial,
                        )
                        verification_url = response.get("verification_url", "")
                        logger.info(f"Professional TSA registered for {pdf_path.name}")
                    except InsufficientCreditsError as e:
                        error_msg = f"Insufficient credits: {e.message}"
                        self.errors.append(f"{pdf_path.name}: {error_msg}")
                        self.file_completed.emit(
                            pdf_path.name,
                            True,
                            f"Signed (free TSA): {output_path.name} - {error_msg}",
                            "",
                        )
                        logger.warning(f"Insufficient credits, stopping: {e}")
                        break
                    except (NetworkError, APIError) as e:
                        logger.warning(
                            f"Professional TSA not available for {pdf_path.name}: {e}. "
                            "PDF signed with free TSA."
                        )

                self.file_completed.emit(
                    pdf_path.name,
                    True,
                    f"Signed successfully: {output_path.name}",
                    verification_url,
                )
            except Exception as e:
                error_msg = str(e)
                self.errors.append(f"{pdf_path.name}: {error_msg}")
                self.file_completed.emit(pdf_path.name, False, error_msg, "")
                logger.error(f"Error signing {pdf_path.name}: {e}")

        self.finished.emit(self.errors)
