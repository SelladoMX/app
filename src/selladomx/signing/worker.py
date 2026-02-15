"""Background worker for PDF signing operations."""
import hashlib
import logging
from pathlib import Path
from typing import List, Optional

from PySide6.QtCore import QThread, Signal

from ..api.client import SelladoMXAPIClient
from ..api.exceptions import (
    AuthenticationError,
    InsufficientCreditsError,
    NetworkError,
    APIError,
)
from ..config import SIGNED_SUFFIX
from .pdf_signer import PDFSigner
from .tsa import APITimeStamper, TSAClient


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
        total = len(self.pdf_paths)

        # For professional TSA: create API client upfront
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

                # Create appropriate timestamper for this file
                api_timestamper = None
                if api_client and self.use_professional_tsa:
                    api_timestamper = APITimeStamper(
                        api_client=api_client,
                        filename=pdf_path.name,
                        size_bytes=pdf_path.stat().st_size,
                        signer_cn=self.signer_cn,
                        signer_serial=self.signer_serial,
                    )

                # Create signer with the appropriate timestamper
                # Each file gets its own PDFSigner because the APITimeStamper
                # is per-file (different filename/size metadata)
                signer = PDFSigner(
                    self.cert,
                    self.private_key,
                    tsa_client=self.tsa_client,
                    timestamper=api_timestamper,
                )

                # Sign — timestamp is now embedded during signing
                output_path = signer.sign_pdf(pdf_path, output_path)

                # After signing: update record with actual file hash
                verification_url = ""
                if api_timestamper and api_timestamper.record_id:
                    file_hash = hashlib.sha256(output_path.read_bytes()).hexdigest()
                    file_size = output_path.stat().st_size
                    try:
                        api_client.complete_timestamp(
                            api_timestamper.record_id, file_hash, file_size
                        )
                    except Exception as e:
                        logger.warning(f"Failed to update record hash: {e}")
                    verification_url = api_timestamper.verification_url or ""
                    logger.info(f"Professional TSA embedded for {pdf_path.name}")

                self.file_completed.emit(
                    pdf_path.name,
                    True,
                    f"Signed successfully: {output_path.name}",
                    verification_url,
                )
            except InsufficientCreditsError:
                error_msg = "No tienes créditos suficientes. Compra más en selladomx.com/precios"
                self.errors.append(f"{pdf_path.name}: {error_msg}")
                self.file_completed.emit(pdf_path.name, False, error_msg, "")
                logger.error(f"Insufficient credits for {pdf_path.name}")
                break
            except AuthenticationError:
                error_msg = "Token inválido o expirado. Reconfigura tu token."
                self.errors.append(f"{pdf_path.name}: {error_msg}")
                self.file_completed.emit(pdf_path.name, False, error_msg, "")
                logger.error(f"Auth error for {pdf_path.name}")
                break
            except (NetworkError, APIError) as e:
                error_msg = (
                    e.message
                    if hasattr(e, "message") and e.message
                    else "Servicio no disponible. Intenta más tarde."
                )
                self.errors.append(f"{pdf_path.name}: {error_msg}")
                self.file_completed.emit(pdf_path.name, False, error_msg, "")
                logger.error(f"TSA service error for {pdf_path.name}: {error_msg}")
                break
            except Exception as e:
                error_msg = str(e)
                self.errors.append(f"{pdf_path.name}: {error_msg}")
                self.file_completed.emit(pdf_path.name, False, error_msg, "")
                logger.error(f"Error signing {pdf_path.name}: {e}")

        self.finished.emit(self.errors)
