"""MainViewModel - Central bridge between Python backend and QML UI."""
import logging
from pathlib import Path
from typing import List, Optional

from PySide6.QtCore import QObject, Signal, Slot, Property, QUrl

from ...signing.certificate_validator import CertificateValidator
from ...errors import CertificateError, CertificateExpiredError, CertificateRevokedError
from ...utils.settings_manager import SettingsManager
from ...config import (
    COLOR_SUCCESS,
    COLOR_ERROR,
    COLOR_WARNING,
    COLOR_INFO,
    COLOR_MUTED,
    COLOR_MUTED_LIGHT,
)
from .signing_coordinator import SigningCoordinator
from .history_view_model import HistoryViewModel

logger = logging.getLogger(__name__)


class MainViewModel(QObject):
    """ViewModel principal que expone toda la lógica a QML.

    This class acts as the bridge between the Python backend and QML frontend.
    It exposes properties and slots that QML can access, and emits signals
    that QML can listen to.
    """

    # Signals for notifying QML of changes
    pdfFilesChanged = Signal()
    step1CompleteChanged = Signal()
    step2CompleteChanged = Signal()
    certPathChanged = Signal()
    keyPathChanged = Signal()
    certStatusChanged = Signal()
    certStatusColorChanged = Signal()
    signingProgressChanged = Signal()
    currentProgressChanged = Signal()
    isSigningChanged = Signal()
    statusLogChanged = Signal()
    useProfessionalTSAChanged = Signal()
    hasProfessionalTSAChanged = Signal()
    creditBalanceChanged = Signal()

    # Signals for token management
    tokensLoaded = Signal(list)
    tokenDerived = Signal(dict)       # {token, alias, expires_at}
    tokenRevoked = Signal(str)        # token_id
    tokenError = Signal(str)          # error message
    isPrimaryTokenChanged = Signal()
    tokensListChanged = Signal()

    # Signals for real-time updates
    fileCompleted = Signal(str, bool, str, str)  # filename, success, message, url
    statusMessage = Signal(str, str)  # message, color
    tokenValidationResult = Signal(bool, str)  # success, message
    signingCompleted = Signal(
        int, int, bool
    )  # success_count, total_count, used_professional_tsa
    showConfirmSigningDialog = Signal(
        int, bool, int
    )  # file_count, use_professional_tsa, credit_balance
    tokenConfiguredViaDeepLink = Signal()
    verificationUrlsReady = Signal(list)  # list of {filename, url} dicts

    def __init__(
        self, settings_manager: SettingsManager, signing_coordinator: SigningCoordinator
    ):
        """Initialize the MainViewModel.

        Args:
            settings_manager: Settings manager instance
            signing_coordinator: Signing coordinator instance
        """
        super().__init__()
        self.settings = settings_manager
        self.coordinator = signing_coordinator

        # Internal state
        self._pdf_files: List[str] = []
        self._step1_complete = False
        self._step2_complete = False
        self._cert_path = ""
        self._key_path = ""
        self._cert_status = "No se ha cargado certificado"
        self._cert_status_color = COLOR_MUTED_LIGHT
        self._signing_progress = 0
        self._current_progress = 0
        self._is_signing = False
        self._status_log = ""
        self._use_professional_tsa = False
        self._credit_balance = 0

        # Token management state
        self._tokens_list: list[dict] = []
        self._is_primary_token: bool = False

        # API client and history view model
        self._api_client: Optional['SelladoMXAPIClient'] = None
        self._history_view_model: Optional[HistoryViewModel] = None

        # Certificate objects
        self.cert = None
        self.private_key = None
        self.signer_cn = ""
        self.signer_serial = ""

        # Verification URLs collected during signing
        self._verification_urls: list[dict] = []
        self._success_count: int = 0

        # Connect coordinator signals
        self.coordinator.progressChanged.connect(self._on_signing_progress)
        self.coordinator.fileCompleted.connect(self._on_file_completed)
        self.coordinator.finished.connect(self._on_signing_finished)

        # Load saved preferences
        self._load_saved_preferences()

        logger.info("MainViewModel initialized")

    def _load_saved_preferences(self):
        """Load saved preferences from settings."""
        # Load last used certificate paths
        self._cert_path = self.settings.get_last_cert_path()
        self._key_path = self.settings.get_last_key_path()

        # Load TSA preference
        self._use_professional_tsa = self.settings.use_professional_tsa()

        # Load cached credit balance
        self._credit_balance = self.settings.get_last_credit_balance()

        # Load token info (primary status)
        token_info = self.settings.get_token_info()
        self._is_primary_token = token_info.get("is_primary", False)

        # Emit signals to update QML
        self.certPathChanged.emit()
        self.keyPathChanged.emit()
        self.useProfessionalTSAChanged.emit()
        self.creditBalanceChanged.emit()
        self.isPrimaryTokenChanged.emit()

    # ========================================================================
    # PDF FILES MANAGEMENT (STEP 1)
    # ========================================================================

    @Slot(list)
    def addPdfFiles(self, file_urls: List[str]):
        """Add PDF files from QML FileDialog.

        Args:
            file_urls: List of file URLs from QML (file:///path/to.pdf)
        """
        for url_str in file_urls:
            url = QUrl(url_str)
            path = url.toLocalFile()
            if path and path not in self._pdf_files:
                self._pdf_files.append(path)
                logger.info(f"Added PDF: {path}")

        self._step1_complete = len(self._pdf_files) > 0
        self.pdfFilesChanged.emit()
        self.step1CompleteChanged.emit()

        self._append_status_log(
            f"✓ {len(file_urls)} archivo(s) agregado(s)", COLOR_SUCCESS
        )

    @Slot()
    def clearPdfList(self):
        """Clear the PDF files list."""
        self._pdf_files.clear()
        self._step1_complete = False
        self.pdfFilesChanged.emit()
        self.step1CompleteChanged.emit()

        self._append_status_log("Lista de PDFs limpiada", COLOR_MUTED)

    @Slot(int)
    def removePdfAt(self, index: int):
        """Remove PDF at specific index.

        Args:
            index: Index of PDF to remove
        """
        if 0 <= index < len(self._pdf_files):
            removed = self._pdf_files.pop(index)
            logger.info(f"Removed PDF: {removed}")
            self._step1_complete = len(self._pdf_files) > 0
            self.pdfFilesChanged.emit()
            self.step1CompleteChanged.emit()

    @Property(list, notify=pdfFilesChanged)
    def pdfFiles(self) -> List[str]:
        """Get list of PDF files (property for QML)."""
        return self._pdf_files

    @Property(int, notify=pdfFilesChanged)
    def pdfCount(self) -> int:
        """Get count of PDF files (property for QML)."""
        return len(self._pdf_files)

    @Property(bool, notify=step1CompleteChanged)
    def step1Complete(self) -> bool:
        """Check if step 1 is complete (property for QML)."""
        return self._step1_complete

    # ========================================================================
    # CERTIFICATE MANAGEMENT (STEP 2)
    # ========================================================================

    @Slot(str)
    def setCertPath(self, file_url: str):
        """Set certificate path from QML FileDialog.

        Args:
            file_url: File URL from QML (file:///path/to.cer)
        """
        url = QUrl(file_url)
        self._cert_path = url.toLocalFile()
        self.settings.set_last_cert_path(self._cert_path)
        self.certPathChanged.emit()

        # Try to validate if both cert and key are set
        if self._cert_path and self._key_path:
            self._append_status_log(
                "Certificado seleccionado. Ingresa la contraseña para validar.",
                COLOR_INFO,
            )

    @Slot(str)
    def setKeyPath(self, file_url: str):
        """Set private key path from QML FileDialog.

        Args:
            file_url: File URL from QML (file:///path/to.key)
        """
        url = QUrl(file_url)
        self._key_path = url.toLocalFile()
        self.settings.set_last_key_path(self._key_path)
        self.keyPathChanged.emit()

        # Try to validate if both cert and key are set
        if self._cert_path and self._key_path:
            self._append_status_log(
                "Llave privada seleccionada. Ingresa la contraseña para validar.",
                COLOR_INFO,
            )

    @Slot(str, str, str)
    def loadCertificate(self, cert_path: str, key_path: str, password: str):
        """Load and validate certificate with password.

        Args:
            cert_path: Path to certificate file
            key_path: Path to private key file
            password: Password for private key
        """
        try:
            logger.info("Validating certificate...")
            validator = CertificateValidator(cert_path, key_path, password)
            self.cert, self.private_key = validator.validate_all()

            # Extract signer info
            subject = self.cert.subject
            for attr in subject:
                if attr.oid._name == "commonName":
                    self.signer_cn = attr.value
                elif attr.oid._name == "serialNumber":
                    self.signer_serial = attr.value

            self._step2_complete = True
            self._cert_status = f"✓ Certificado válido: {self.signer_cn}"
            self._cert_status_color = COLOR_SUCCESS

            self.step2CompleteChanged.emit()
            self.certStatusChanged.emit()
            self.certStatusColorChanged.emit()

            self._append_status_log(
                f"✓ Certificado válido: {self.signer_cn}", COLOR_SUCCESS
            )

            logger.info(f"Certificate validated: {self.signer_cn}")

        except CertificateExpiredError as e:
            self._handle_cert_error(f"✗ Certificado expirado: {e}", COLOR_WARNING)
        except CertificateRevokedError as e:
            self._handle_cert_error(f"✗ Certificado revocado: {e}", COLOR_ERROR)
        except CertificateError as e:
            self._handle_cert_error(f"✗ Error de certificado: {e}", COLOR_ERROR)
        except Exception as e:
            self._handle_cert_error(f"✗ Error inesperado: {e}", COLOR_ERROR)

    def _handle_cert_error(self, message: str, color: str):
        """Handle certificate validation error.

        Args:
            message: Error message
            color: Color for the message
        """
        self._step2_complete = False
        self._cert_status = message
        self._cert_status_color = color

        self.step2CompleteChanged.emit()
        self.certStatusChanged.emit()
        self.certStatusColorChanged.emit()

        self._append_status_log(message, color)

        logger.error(message)

    @Property(str, notify=certPathChanged)
    def certPath(self) -> str:
        """Get certificate path (property for QML)."""
        return self._cert_path

    @Property(str, notify=keyPathChanged)
    def keyPath(self) -> str:
        """Get private key path (property for QML)."""
        return self._key_path

    @Property(str, notify=certStatusChanged)
    def certStatus(self) -> str:
        """Get certificate status message (property for QML)."""
        return self._cert_status

    @Property(str, notify=certStatusColorChanged)
    def certStatusColor(self) -> str:
        """Get certificate status color (property for QML)."""
        return self._cert_status_color

    @Property(bool, notify=step2CompleteChanged)
    def step2Complete(self) -> bool:
        """Check if step 2 is complete (property for QML)."""
        return self._step2_complete

    # ========================================================================
    # SIGNING PROCESS (STEP 3)
    # ========================================================================

    @Slot()
    def confirmSigning(self):
        """Show confirmation dialog before signing starts."""
        if not self._step1_complete or not self._step2_complete:
            self._append_status_log(
                "✗ Completa los pasos anteriores primero", COLOR_ERROR
            )
            return

        self.showConfirmSigningDialog.emit(
            len(self._pdf_files),
            self._use_professional_tsa,
            self._credit_balance,
        )

    @Slot()
    def startSigning(self):
        """Start the signing process."""
        if not self._step1_complete or not self._step2_complete:
            self._append_status_log(
                "✗ Completa los pasos anteriores primero", COLOR_ERROR
            )
            return

        if self._is_signing:
            logger.warning("Signing already in progress")
            return

        self._is_signing = True
        self._current_progress = 0
        self._status_log = ""
        self._verification_urls = []
        self._success_count = 0
        self.isSigningChanged.emit()
        self.currentProgressChanged.emit()
        self.statusLogChanged.emit()

        # Get API key if using professional TSA
        api_key = None
        if self._use_professional_tsa:
            api_key = self.settings.get_token()
            if not api_key:
                self._append_status_log(
                    "✗ No se encontró token para TSA Profesional", COLOR_ERROR
                )
                self._is_signing = False
                self.isSigningChanged.emit()
                return

        # Convert paths to Path objects
        pdf_paths = [Path(p) for p in self._pdf_files]

        self._append_status_log(
            f"Iniciando firma de {len(pdf_paths)} documento(s)...", COLOR_INFO
        )

        # Start signing
        self.coordinator.start(
            pdf_paths=pdf_paths,
            cert=self.cert,
            private_key=self.private_key,
            use_professional_tsa=self._use_professional_tsa,
            api_key=api_key,
            signer_cn=self.signer_cn,
            signer_serial=self.signer_serial,
        )

    def _on_signing_progress(self, current: int, total: int):
        """Handle signing progress update.

        Args:
            current: Current file number
            total: Total files
        """
        self._current_progress = current
        self._signing_progress = total
        self.currentProgressChanged.emit()
        self.signingProgressChanged.emit()

        self._append_status_log(f"Progreso: {current}/{total}", COLOR_INFO)

    def _on_file_completed(
        self, filename: str, success: bool, message: str, verification_url: str
    ):
        """Handle file completion.

        Args:
            filename: Name of the file
            success: Whether signing was successful
            message: Status message
            verification_url: Verification URL (if professional TSA)
        """
        color = COLOR_SUCCESS if success else COLOR_ERROR
        self._append_status_log(message, color)

        if success:
            self._success_count += 1

        # Collect verification URLs for the success dialog
        if verification_url:
            self._verification_urls.append(
                {"filename": filename, "url": verification_url}
            )

        # Emit signal for QML to handle (e.g., show link button)
        self.fileCompleted.emit(filename, success, message, verification_url)

    def _on_signing_finished(self, errors: List[str]):
        """Handle signing completion.

        Args:
            errors: List of error messages
        """
        self._is_signing = False
        self.isSigningChanged.emit()

        total_count = len(self._pdf_files)
        success_count = self._success_count

        if errors:
            self._append_status_log(
                f"✗ Firmado completado con {len(errors)} error(es)", COLOR_WARNING
            )
        else:
            self._append_status_log(
                "✓ Todos los documentos firmados exitosamente", COLOR_SUCCESS
            )

        # Emit verification URLs if any were collected
        if self._verification_urls:
            self.verificationUrlsReady.emit(self._verification_urls)

        # Emit completion signal for QML to show appropriate dialog
        self.signingCompleted.emit(
            success_count, total_count, self._use_professional_tsa
        )

        # Refresh credit balance if professional TSA was used
        if self._use_professional_tsa:
            self._refresh_credit_balance()

    def _append_status_log(self, message: str, color: str):
        """Append message to status log with color.

        Args:
            message: Message to append
            color: HTML color code
        """
        timestamp = ""  # Could add timestamp if needed
        html = f'<span style="color: {color};">{message}</span><br>'
        self._status_log += html
        self.statusLogChanged.emit()

        # Also emit individual status message
        self.statusMessage.emit(message, color)

    @Property(int, notify=currentProgressChanged)
    def currentProgress(self) -> int:
        """Get current signing progress (property for QML)."""
        return self._current_progress

    @Property(int, notify=signingProgressChanged)
    def signingProgress(self) -> int:
        """Get total signing progress (property for QML)."""
        return self._signing_progress

    @Property(bool, notify=isSigningChanged)
    def isSigning(self) -> bool:
        """Check if signing is in progress (property for QML)."""
        return self._is_signing

    @Property(str, notify=statusLogChanged)
    def statusLog(self) -> str:
        """Get status log HTML (property for QML)."""
        return self._status_log

    # ========================================================================
    # TSA AND CREDITS (STEP 3)
    # ========================================================================

    @Slot(bool)
    def setUseProfessionalTSA(self, enabled: bool):
        """Set whether to use professional TSA.

        Args:
            enabled: True to use professional TSA
        """
        self._use_professional_tsa = enabled
        self.settings.set_use_professional_tsa(enabled)
        self.useProfessionalTSAChanged.emit()

        logger.info(f"Professional TSA: {enabled}")

    @Slot()
    def refreshCreditBalance(self):
        """Refresh credit balance from API."""
        self._refresh_credit_balance()

    def _refresh_credit_balance(self):
        """Refresh credit balance from API (internal)."""
        from ...api.client import SelladoMXAPIClient
        from ...api.exceptions import APIError

        api_key = self.settings.get_token()
        if not api_key:
            self._credit_balance = 0
            self.creditBalanceChanged.emit()
            self.hasProfessionalTSAChanged.emit()
            return

        try:
            client = SelladoMXAPIClient(api_key=api_key)
            response = client.get_balance()
            self._credit_balance = response.get("credits_remaining", 0)
            self.settings.set_last_credit_balance(self._credit_balance)
            self.creditBalanceChanged.emit()
            self.hasProfessionalTSAChanged.emit()

            logger.info(f"Credit balance updated: {self._credit_balance}")
        except APIError as e:
            logger.error(f"Failed to refresh credit balance: {e}")

    @Property(bool, notify=useProfessionalTSAChanged)
    def useProfessionalTSA(self) -> bool:
        """Check if using professional TSA (property for QML)."""
        return self._use_professional_tsa

    @Property(bool, notify=hasProfessionalTSAChanged)
    def hasProfessionalTSA(self) -> bool:
        """Check if professional TSA is available (property for QML)."""
        return self.settings.has_api_key()

    @Property(int, notify=creditBalanceChanged)
    def creditBalance(self) -> int:
        """Get credit balance (property for QML)."""
        return self._credit_balance

    # ========================================================================
    # TOKEN CONFIGURATION
    # ========================================================================

    @Slot(str)
    def validateAndSaveToken(self, token: str):
        """Validate and save the API token.

        Args:
            token: The API token to validate
        """
        from ...api.client import SelladoMXAPIClient
        from ...api.exceptions import APIError, AuthenticationError, NetworkError

        try:
            # Validate token with API
            client = SelladoMXAPIClient(api_key=token)
            response = client.get_balance()

            # Save token and metadata
            self.settings.set_token(token)
            if "token_info" in response:
                self.settings.set_token_info(response["token_info"])
                self._is_primary_token = response["token_info"].get("is_primary", False)
                self.isPrimaryTokenChanged.emit()
            self.settings.set_last_credit_balance(response["credits_remaining"])

            # Update internal state
            self._credit_balance = response["credits_remaining"]
            self.creditBalanceChanged.emit()

            # Reset history view model to force re-creation with new token
            self._api_client = None
            self._history_view_model = None
            self.hasProfessionalTSAChanged.emit()

            # Emit success
            message = f"✅ Token configurado exitosamente\n{response['credits_remaining']} créditos disponibles"
            self.tokenValidationResult.emit(True, message)

            logger.info(
                f"Token validated successfully, {response['credits_remaining']} credits available"
            )

        except AuthenticationError as e:
            message = f"❌ Token inválido: {e.message}"
            self.tokenValidationResult.emit(False, message)
            logger.error(f"Token validation failed: {e}")
        except NetworkError as e:
            message = f"❌ Error de red: {e.message}"
            self.tokenValidationResult.emit(False, message)
            logger.error(f"Network error during token validation: {e}")
        except APIError as e:
            message = f"❌ Error del servidor: {e.message}"
            self.tokenValidationResult.emit(False, message)
            logger.error(f"API error during token validation: {e}")
        except Exception as e:
            message = f"❌ Error inesperado: {str(e)}"
            self.tokenValidationResult.emit(False, message)
            logger.error(f"Unexpected error during token validation: {e}")

    # ========================================================================
    # TOKEN MANAGEMENT (SUBTOKENS)
    # ========================================================================

    @Property(list, notify=tokensListChanged)
    def tokensList(self) -> list:
        """Get list of derived tokens (property for QML)."""
        return self._tokens_list

    @Property(bool, notify=isPrimaryTokenChanged)
    def isPrimaryToken(self) -> bool:
        """Check if current token is a primary token (property for QML)."""
        return self._is_primary_token

    @Property(QObject, constant=False, notify=hasProfessionalTSAChanged)
    def historyViewModel(self) -> Optional[HistoryViewModel]:
        """Get history view model (lazy-loaded when API client is available)."""
        if self._history_view_model is None and self.settings.has_api_key():
            from ...api.client import SelladoMXAPIClient
            api_key = self.settings.get_token()
            if api_key:
                self._api_client = SelladoMXAPIClient(api_key=api_key)
                self._history_view_model = HistoryViewModel(self._api_client)
        return self._history_view_model

    @Slot()
    def listTokens(self):
        """List all tokens for the current user."""
        from ...api.client import SelladoMXAPIClient
        from ...api.exceptions import APIError

        api_key = self.settings.get_token()
        if not api_key:
            self.tokenError.emit("No se encontró token configurado")
            return

        try:
            client = SelladoMXAPIClient(api_key=api_key)
            response = client.list_tokens()
            self._tokens_list = response.get("derived", [])
            self.tokensListChanged.emit()
            self.tokensLoaded.emit(self._tokens_list)
            logger.info(f"Loaded {len(self._tokens_list)} derived tokens")
        except APIError as e:
            logger.error(f"Failed to list tokens: {e}")
            self.tokenError.emit(f"Error al cargar subtokens: {e.message}")

    @Slot(str, int)
    def deriveToken(self, alias: str, expires_in_days: int):
        """Create a derived token.

        Args:
            alias: User-friendly name for the token
            expires_in_days: Expiration in days (0 = no expiration)
        """
        from ...api.client import SelladoMXAPIClient
        from ...api.exceptions import APIError, PrimaryTokenRequiredError

        api_key = self.settings.get_token()
        if not api_key:
            self.tokenError.emit("No se encontró token configurado")
            return

        try:
            client = SelladoMXAPIClient(api_key=api_key)
            expires = expires_in_days if expires_in_days > 0 else None
            response = client.derive_token(alias, expires)
            self.tokenDerived.emit(response)
            logger.info(f"Derived token created: {alias}")
            # Refresh the list
            self.listTokens()
        except PrimaryTokenRequiredError:
            self.tokenError.emit("Se requiere el token primario para crear subtokens")
        except APIError as e:
            logger.error(f"Failed to derive token: {e}")
            self.tokenError.emit(f"Error al crear subtoken: {e.message}")

    @Slot(str)
    def revokeToken(self, token_id: str):
        """Revoke a token by ID.

        Args:
            token_id: UUID of the token to revoke
        """
        from ...api.client import SelladoMXAPIClient
        from ...api.exceptions import APIError

        api_key = self.settings.get_token()
        if not api_key:
            self.tokenError.emit("No se encontró token configurado")
            return

        try:
            client = SelladoMXAPIClient(api_key=api_key)
            client.revoke_token(token_id)
            self.tokenRevoked.emit(token_id)
            logger.info(f"Token revoked: {token_id}")
            # Refresh the list
            self.listTokens()
        except APIError as e:
            logger.error(f"Failed to revoke token: {e}")
            self.tokenError.emit(f"Error al revocar subtoken: {e.message}")

    # ========================================================================
    # DEEP LINK HANDLING
    # ========================================================================

    @Slot(str)
    def handleDeepLink(self, url: str):
        """Handle deep link URL.

        Args:
            url: Deep link URL (selladomx://token?value=xxx)
        """
        logger.info(f"Handling deep link: {url}")

        # Extract token from URL
        # This will be connected to DeepLinkHandler in main.py
        # For now, just log it
        self._append_status_log("Deep link recibido - procesando...", COLOR_INFO)
