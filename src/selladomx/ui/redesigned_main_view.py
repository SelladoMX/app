"""Redesigned main view with guided workflow (Balena Etcher style)."""
import logging
import webbrowser
from pathlib import Path
from typing import Optional, List

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QLineEdit, QProgressBar, QTextBrowser,
    QLabel, QFileDialog, QMessageBox, QScrollArea, QCheckBox, QApplication,
)

from .design_tokens import Colors, Typography, Spacing, BorderRadius

from .widgets.step_widget import StepWidget, StepState
from .api_key_dialog import ApiKeyDialog, ApiTestWorker
from ..signing.certificate_validator import CertificateValidator
from ..signing.pdf_signer import PDFSigner
from ..signing.tsa import TSAClient
from ..errors import (
    CertificateError, CertificateExpiredError, CertificateRevokedError,
)
from ..config import BUY_CREDITS_URL, CREDIT_PRICE_DISPLAY
from ..utils.settings_manager import SettingsManager
from ..api.exceptions import AuthenticationError, InsufficientCreditsError, NetworkError

# Import SigningWorker from signing package
from ..signing.worker import SigningWorker

logger = logging.getLogger(__name__)


class RedesignedMainView(QMainWindow):
    """Redesigned main window with guided 3-step workflow."""

    def __init__(self):
        """Initialize redesigned main view."""
        super().__init__()
        self.cert = None
        self.private_key = None
        self.signing_worker = None
        self.output_dir = None  # Carpeta de destino para PDFs firmados
        self.settings_manager = SettingsManager()
        self._balance_worker = None
        self._used_professional_tsa = False

        self._setup_ui()
        self._connect_signals()
        self._init_step_states()

        # Refresh balance in background
        self._refresh_balance_async()

        logger.info("RedesignedMainView initialized")

    def _setup_ui(self):
        """Setup the user interface."""
        self.setWindowTitle("SelladoMX - Firma Digital de PDFs")
        self.resize(950, 750)
        self.setMinimumSize(900, 700)

        # Central widget with scroll area
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(0)

        # Header bar (credits & settings)
        self._setup_header_bar(main_layout)

        # Scroll area for steps
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)

        scroll_content = QWidget()
        self.steps_layout = QVBoxLayout(scroll_content)
        self.steps_layout.setSpacing(16)
        self.steps_layout.setContentsMargins(0, 0, 0, 0)

        # STEP 1: Select PDFs
        self.step1 = StepWidget(
            1,
            "Seleccionar PDFs",
            "Agrega los documentos que deseas firmar"
        )
        self._setup_step1_content()
        self.steps_layout.addWidget(self.step1)

        # STEP 2: Load Certificate
        self.step2 = StepWidget(
            2,
            "Cargar Certificado",
            "Selecciona tu certificado e.firma y llave privada"
        )
        self._setup_step2_content()
        self.steps_layout.addWidget(self.step2)

        # STEP 3: Sign
        self.step3 = StepWidget(
            3,
            "Firmar",
            "Inicia el proceso de firma digital"
        )
        self._setup_step3_content()
        self.steps_layout.addWidget(self.step3)

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

    def _setup_header_bar(self, parent_layout):
        """Setup the header bar with credits info and settings."""
        header = QWidget()
        header.setStyleSheet(
            f"""
            QWidget {{
                background-color: {Colors.BG_SECONDARY};
                border-bottom: 1px solid {Colors.BORDER_DEFAULT};
            }}
            """
        )
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(Spacing.LG, Spacing.SM, Spacing.LG, Spacing.SM)
        header_layout.setSpacing(Spacing.MD)

        # Credits label (clickable button when free tier)
        self.label_credits = QPushButton("Usando TSA Gratuito • Mejorar a validez legal →")
        self.label_credits.setFlat(True)
        self.label_credits.setStyleSheet(
            f"font-size: {Typography.FONT_SM}px; color: {Colors.TEXT_PRIMARY}; border: none; text-align: left; text-decoration: underline;"
        )
        self.label_credits.setCursor(Qt.PointingHandCursor)
        header_layout.addWidget(self.label_credits)

        # Buy credits button (only shown when already have credits but running low)
        self.btn_buy_credits = QPushButton("💳 Comprar más")
        self.btn_buy_credits.setCursor(Qt.PointingHandCursor)
        self.btn_buy_credits.setProperty("class", "secondary")
        self.btn_buy_credits.setMinimumHeight(32)
        self.btn_buy_credits.setVisible(False)  # Hidden by default, shown when needed
        header_layout.addWidget(self.btn_buy_credits)

        header_layout.addStretch()

        # Settings button
        self.btn_settings = QPushButton("⚙️ Configuración")
        self.btn_settings.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {Colors.SURFACE_DEFAULT};
                color: {Colors.TEXT_PRIMARY};
                border: 2px solid {Colors.BORDER_DEFAULT};
                border-radius: {BorderRadius.MD}px;
                padding: {Spacing.XS}px {Spacing.MD}px;
                font-size: {Typography.FONT_SM}px;
            }}
            QPushButton:hover {{
                background-color: {Colors.BG_ELEVATED};
            }}
            """
        )
        header_layout.addWidget(self.btn_settings)

        parent_layout.addWidget(header)

        # Update the label based on current settings
        self._update_credit_label()

    def _setup_step1_content(self):
        """Setup content for step 1 (Select PDFs)."""
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # PDF list
        self.list_pdfs = QListWidget()
        self.list_pdfs.setMinimumHeight(150)
        layout.addWidget(self.list_pdfs)

        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        self.btn_add_files = QPushButton("Agregar PDFs...")
        self.btn_clear_files = QPushButton("Limpiar lista")
        self.btn_clear_files.setProperty("class", "secondary")

        buttons_layout.addWidget(self.btn_add_files)
        buttons_layout.addWidget(self.btn_clear_files)
        buttons_layout.addStretch()

        layout.addLayout(buttons_layout)

        # Credit cost estimation
        self.label_credit_estimate = QLabel("")
        self.label_credit_estimate.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: {Typography.FONT_BASE}px; margin-top: {Spacing.SM}px;"
        )
        self.label_credit_estimate.setWordWrap(True)
        layout.addWidget(self.label_credit_estimate)

        self.step1.set_content(content)

    def _setup_step2_content(self):
        """Setup content for step 2 (Load Certificate)."""
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        # Certificate .cer
        cert_row = QHBoxLayout()
        cert_row.addWidget(QLabel("Certificado (.cer):"))
        self.line_cert_path = QLineEdit()
        self.line_cert_path.setReadOnly(True)
        self.line_cert_path.setPlaceholderText("Selecciona tu certificado...")
        cert_row.addWidget(self.line_cert_path)
        self.btn_browse_cert = QPushButton("Seleccionar")
        self.btn_browse_cert.setMaximumWidth(120)
        cert_row.addWidget(self.btn_browse_cert)
        layout.addLayout(cert_row)

        # Private key .key
        key_row = QHBoxLayout()
        key_row.addWidget(QLabel("Clave privada (.key):"))
        self.line_key_path = QLineEdit()
        self.line_key_path.setReadOnly(True)
        self.line_key_path.setPlaceholderText("Selecciona tu llave privada...")
        key_row.addWidget(self.line_key_path)
        self.btn_browse_key = QPushButton("Seleccionar")
        self.btn_browse_key.setMaximumWidth(120)
        key_row.addWidget(self.btn_browse_key)
        layout.addLayout(key_row)

        # Password
        password_row = QHBoxLayout()
        password_row.addWidget(QLabel("Contrase\u00f1a:"))
        self.line_password = QLineEdit()
        self.line_password.setEchoMode(QLineEdit.Password)
        self.line_password.setPlaceholderText("Ingresa tu contrase\u00f1a...")
        password_row.addWidget(self.line_password)
        layout.addLayout(password_row)

        # Validation status
        self.label_cert_status = QLabel("Esperando certificado...")
        self.label_cert_status.setProperty("class", "secondary")
        self.label_cert_status.setWordWrap(True)
        layout.addWidget(self.label_cert_status)

        self.step2.set_content(content)

        # Auto-populate with last used certificate paths if they exist
        last_cert = self.settings_manager.get_last_cert_path()
        if last_cert and Path(last_cert).exists():
            self.line_cert_path.setText(last_cert)
            logger.info(f"Auto-populated certificate path: {last_cert}")

        last_key = self.settings_manager.get_last_key_path()
        if last_key and Path(last_key).exists():
            self.line_key_path.setText(last_key)
            logger.info(f"Auto-populated key path: {last_key}")

        # Trigger field check to update step 2 state if both paths are populated
        if last_cert and last_key:
            self._check_step2_fields()

    def _setup_step3_content(self):
        """Setup content for step 3 (Sign)."""
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimumHeight(30)
        layout.addWidget(self.progress_bar)

        # Status log (QTextBrowser for clickable links)
        log_label = QLabel("Registro de actividad:")
        log_label.setProperty("class", "secondary")
        layout.addWidget(log_label)

        self.text_status = QTextBrowser()
        self.text_status.setReadOnly(True)
        self.text_status.setOpenExternalLinks(True)
        self.text_status.setMaximumHeight(120)
        layout.addWidget(self.text_status)

        # Output directory selector
        output_row = QHBoxLayout()
        output_row.setSpacing(10)
        output_label = QLabel("Guardar en:")
        output_label.setProperty("class", "secondary")
        output_row.addWidget(output_label)

        self.line_output_dir = QLineEdit()
        self.line_output_dir.setReadOnly(True)
        self.line_output_dir.setPlaceholderText("Misma carpeta que el PDF original (por defecto)")
        output_row.addWidget(self.line_output_dir)

        self.btn_browse_output = QPushButton("Seleccionar carpeta...")
        self.btn_browse_output.setProperty("class", "secondary")
        self.btn_browse_output.setMaximumWidth(160)
        output_row.addWidget(self.btn_browse_output)

        layout.addLayout(output_row)

        # Proactive benefits banner (always visible, not reactive)
        benefits_banner = QWidget()
        benefits_banner.setStyleSheet(
            f"""
            QWidget {{
                background-color: {Colors.BG_PRIMARY};
                border: 2px solid {Colors.BORDER_DEFAULT};
                border-radius: {BorderRadius.LG}px;
                padding: {Spacing.MD}px;
            }}
            """
        )
        benefits_layout = QHBoxLayout(benefits_banner)
        benefits_layout.setContentsMargins(Spacing.MD, Spacing.MD, Spacing.MD, Spacing.MD)
        benefits_layout.setSpacing(Spacing.MD)

        icon_label = QLabel("⚖️")
        icon_label.setStyleSheet(f"font-size: {Typography.FONT_3XL}px;")
        benefits_layout.addWidget(icon_label)

        benefits_text = QLabel(
            "<b>¿Documento legal o empresarial?</b><br/>"
            "TSA Profesional te da validez legal certificada por solo $2 MXN."
        )
        benefits_text.setWordWrap(True)
        benefits_text.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: {Typography.FONT_BASE}px;")
        benefits_layout.addWidget(benefits_text, 1)

        layout.addWidget(benefits_banner)

        # Professional TSA checkbox
        tsa_row = QHBoxLayout()
        tsa_row.setSpacing(8)

        self.chk_professional_tsa = QCheckBox("🔒 Usar TSA Profesional - Validez legal garantizada")
        self.chk_professional_tsa.setEnabled(self.settings_manager.has_api_key())
        self.chk_professional_tsa.setChecked(self.settings_manager.use_professional_tsa())
        tsa_row.addWidget(self.chk_professional_tsa)

        self.label_tsa_credits = QPushButton("")
        self.label_tsa_credits.setFlat(True)
        self.label_tsa_credits.setStyleSheet(
            f"font-size: {Typography.FONT_SM}px; color: {Colors.TEXT_TERTIARY}; border: none; text-align: left; padding: 0;"
        )
        self.label_tsa_credits.setCursor(Qt.ArrowCursor)  # Will be changed to pointer when clickable
        tsa_row.addWidget(self.label_tsa_credits)
        tsa_row.addStretch()

        layout.addLayout(tsa_row)

        self._update_tsa_credits_label()

        # Sign button
        self.btn_sign = QPushButton("Firmar PDFs")
        self.btn_sign.setProperty("class", "success")
        self.btn_sign.setEnabled(False)
        self.btn_sign.setMinimumHeight(50)
        self.btn_sign.setStyleSheet(
            f"""
            QPushButton {{
                font-size: {Typography.FONT_XL}px;
                font-weight: {Typography.WEIGHT_SEMIBOLD};
            }}
            """
        )
        layout.addWidget(self.btn_sign)

        self.step3.set_content(content)

    def _init_step_states(self):
        """Initialize step states."""
        # Step 1 is active by default
        self.step1.state = StepState.ACTIVE

        # Steps 2 and 3 are disabled
        self.step2.state = StepState.DISABLED
        self.step3.state = StepState.DISABLED

    def _connect_signals(self):
        """Connect widget signals."""
        # Step 1 signals
        self.btn_add_files.clicked.connect(self._on_add_files)
        self.btn_clear_files.clicked.connect(self._on_clear_files)
        self.btn_browse_output.clicked.connect(self._on_browse_output)
        self.list_pdfs.itemSelectionChanged.connect(self._check_step1_completion)

        # Step 2 signals - solo verificar campos llenos, no validar
        self.btn_browse_cert.clicked.connect(self._on_browse_cert)
        self.btn_browse_key.clicked.connect(self._on_browse_key)
        self.line_password.textChanged.connect(self._check_step2_fields)

        # Step 3 signals
        self.btn_sign.clicked.connect(self._on_sign_clicked)
        self.chk_professional_tsa.stateChanged.connect(self._on_tsa_preference_changed)

        # Header signals
        self.btn_settings.clicked.connect(self._on_open_settings)
        self.btn_buy_credits.clicked.connect(self._on_buy_credits)
        self.label_credits.clicked.connect(self._on_credits_label_clicked)
        self.label_tsa_credits.clicked.connect(self._on_tsa_credits_label_clicked)

        # Step completion signals
        self.step1.step_completed.connect(self._on_step1_completed)
        self.step2.step_completed.connect(self._on_step2_completed)

    # ========================================================================
    # Header / Credits Methods
    # ========================================================================

    def _update_credit_label(self):
        """Update the credits label based on current settings."""
        if self.settings_manager.has_api_key():
            # Check if token is expired
            if self.settings_manager.is_token_expired():
                self.label_credits.setText("⚠️ Token expirado")
                self.label_credits.setStyleSheet(
                    f"font-size: {Typography.FONT_SM}px; color: {Colors.ERROR}; "
                    f"font-weight: {Typography.WEIGHT_MEDIUM}; border: none;"
                )
                self.btn_buy_credits.setVisible(False)
                return

            balance = self.settings_manager.get_last_credit_balance()

            # Get token info for display
            token_info = self.settings_manager.get_token_info()
            is_primary = token_info.get("is_primary", True)
            alias = token_info.get("alias")

            # Show credits with token type indicator
            label_text = f"Créditos disponibles: {balance}"
            if not is_primary and alias:
                label_text += f" ({alias})"

            self.label_credits.setText(label_text)

            # Color code based on balance and show buy button when low
            if balance < 5:
                self.label_credits.setStyleSheet(
                    f"font-size: {Typography.FONT_SM}px; color: {Colors.WARNING}; "
                    f"font-weight: {Typography.WEIGHT_MEDIUM}; border: none;"
                )
                self.label_credits.setCursor(Qt.ArrowCursor)
                self.btn_buy_credits.setVisible(True)  # Show buy button when low
            else:
                self.label_credits.setStyleSheet(
                    f"font-size: {Typography.FONT_SM}px; color: {Colors.SUCCESS}; "
                    f"font-weight: {Typography.WEIGHT_MEDIUM}; border: none;"
                )
                self.label_credits.setCursor(Qt.ArrowCursor)
                self.btn_buy_credits.setVisible(False)  # Hide when have enough
        else:
            # Free tier - show upgrade message
            self.label_credits.setText("Usando TSA Gratuito • Mejorar validez legal →")
            self.label_credits.setStyleSheet(
                f"font-size: {Typography.FONT_SM}px; color: {Colors.TEXT_PRIMARY}; border: none; "
                "text-decoration: underline;"
            )
            self.label_credits.setCursor(Qt.PointingHandCursor)
            self.btn_buy_credits.setVisible(False)  # Hide buy button on free tier

    def _update_tsa_credits_label(self):
        """Update the TSA credits label next to the checkbox."""
        if self.settings_manager.has_api_key():
            balance = self.settings_manager.get_last_credit_balance()
            if balance > 0:
                self.label_tsa_credits.setText(f"({balance} créditos disponibles)")
                self.label_tsa_credits.setStyleSheet(
                    f"font-size: {Typography.FONT_SM}px; color: {Colors.SUCCESS}; border: none; text-align: left; padding: 0;"
                )
                self.label_tsa_credits.setCursor(Qt.ArrowCursor)
                self.label_tsa_credits.setVisible(True)
            else:
                self.label_tsa_credits.setText("(sin créditos - compra aquí)")
                self.label_tsa_credits.setStyleSheet(
                    f"font-size: {Typography.FONT_SM}px; color: {Colors.INFO}; border: none; text-align: left; padding: 0; text-decoration: underline;"
                )
                self.label_tsa_credits.setCursor(Qt.PointingHandCursor)
                self.label_tsa_credits.setVisible(True)
        else:
            # Hide the label when no API key
            self.label_tsa_credits.setText("")
            self.label_tsa_credits.setVisible(False)

    def _update_credit_estimate(self):
        """Update credit cost estimation based on PDF count."""
        from ..config import CREDIT_PRICE_MXN

        pdf_count = self.list_pdfs.count()
        if pdf_count > 0:
            cost = pdf_count * CREDIT_PRICE_MXN
            self.label_credit_estimate.setText(
                f"💰 Costo con TSA Profesional: {pdf_count} × ${CREDIT_PRICE_MXN} = ${cost} MXN"
            )
        else:
            self.label_credit_estimate.clear()

    def _on_open_settings(self):
        """Show settings menu with options."""
        from PySide6.QtWidgets import QMenu

        menu = QMenu(self)

        # Option 1: Manual token config
        action_config = menu.addAction("Configurar token manualmente")
        action_config.triggered.connect(self._on_open_api_key_dialog)

        # Option 2: Token management (only if has token and is primary)
        if self.settings_manager.has_api_key():
            token_info = self.settings_manager.get_token_info()
            if token_info.get("is_primary", False):
                action_manage = menu.addAction("Administrar tokens")
                action_manage.triggered.connect(self._on_open_token_management)

        # Option 3: Clear saved certificate paths
        menu.addSeparator()
        action_clear_paths = menu.addAction("Limpiar rutas de certificados guardadas")
        action_clear_paths.triggered.connect(self._on_clear_certificate_paths)

        menu.exec(self.btn_settings.mapToGlobal(self.btn_settings.rect().bottomLeft()))

    def _on_open_api_key_dialog(self):
        """Open API key dialog."""
        dialog = ApiKeyDialog(self.settings_manager, self)
        dialog.exec()
        # Refresh UI after dialog closes
        self._update_credit_label()
        self._update_tsa_credits_label()
        self.chk_professional_tsa.setEnabled(self.settings_manager.has_api_key())
        if not self.settings_manager.has_api_key():
            self.chk_professional_tsa.setChecked(False)
        self._refresh_balance_async()

    def _on_open_token_management(self):
        """Open token management dialog."""
        from .token_management_dialog import TokenManagementDialog
        dialog = TokenManagementDialog(self.settings_manager, self)
        dialog.exec()
        self._refresh_balance_async()

    def _on_clear_certificate_paths(self):
        """Clear saved certificate paths."""
        self.settings_manager.clear_certificate_paths()
        self.line_cert_path.clear()
        self.line_key_path.clear()
        self._check_step2_fields()
        QMessageBox.information(
            self,
            "Rutas limpiadas",
            "Las rutas de certificados guardadas han sido eliminadas."
        )

    def _on_credits_label_clicked(self):
        """Show benefits dialog when user clicks on free TSA label."""
        # Only show benefits if they don't have a token configured
        if not self.settings_manager.has_api_key():
            self._show_upgrade_benefits_dialog()
        # If they have credits but are low, also show
        elif self.settings_manager.get_last_credit_balance() < 5:
            self._show_upgrade_benefits_dialog()

    def _show_upgrade_benefits_dialog(self):
        """Show a persuasive dialog about TSA Professional benefits."""
        dialog = QMessageBox(self)
        dialog.setWindowTitle("Mejora tu Seguridad Legal")
        dialog.setIcon(QMessageBox.Information)

        message = f"""
<h3 style="color: {Colors.PRIMARY};">🔒 TSA Profesional - Máxima Seguridad Legal</h3>

<p><b>¿Por qué necesitas TSA Profesional?</b></p>

<table style="width: 100%; margin: 10px 0;">
    <tr>
        <td style="padding: 8px; background: {Colors.SUCCESS_LIGHT};">
            <b style="color: {Colors.SUCCESS};">✓ TSA Profesional</b><br/>
            <span style="font-size: 12px; color: {Colors.TEXT_SECONDARY};">
            • Validez legal garantizada por DigitalSign<br/>
            • Certificación oficial RFC 3161<br/>
            • Hash registrado y verificable en selladomx.com<br/>
            • Fecha y hora certificada por terceros<br/>
            • Evidencia admisible en juicios<br/>
            • Cumplimiento NOM-151-SCFI-2016
            </span>
        </td>
    </tr>
    <tr>
        <td style="padding: 8px; background: {Colors.ERROR_LIGHT};">
            <b style="color: {Colors.ERROR};">⚠️ TSA Gratuito</b><br/>
            <span style="font-size: 12px; color: {Colors.TEXT_SECONDARY};">
            • ⚠️ Sin registro de hash<br/>
            • ⚠️ Validez limitada (sin garantía)<br/>
            • ❌ No certificado por terceros<br/>
            • ❌ Fecha no verificable por terceros<br/>
            • ⚠️ Aceptación limitada en procesos legales<br/>
            • Recomendado para documentos internos
            </span>
        </td>
    </tr>
</table>

<p style="margin-top: 15px;">
<b>💰 Solo {CREDIT_PRICE_DISPLAY} por documento</b><br/>
<span style="font-size: 12px; color: #666;">Protege tu patrimonio y negocios con la máxima seguridad.</span>
</p>
        """

        dialog.setText(message)
        dialog.setTextFormat(Qt.RichText)

        # Add custom buttons
        btn_buy = dialog.addButton("Comprar Créditos", QMessageBox.AcceptRole)
        btn_cancel = dialog.addButton("Ahora No", QMessageBox.RejectRole)

        dialog.exec()

        clicked = dialog.clickedButton()
        if clicked == btn_buy:
            webbrowser.open(BUY_CREDITS_URL)

    def _show_signing_success_dialog(self, signed_count: int, used_pro_tsa: bool):
        """Show success dialog with appropriate messaging based on TSA tier used."""
        dialog = QMessageBox(self)
        dialog.setWindowTitle("✅ Firma Completa")
        dialog.setIcon(QMessageBox.Information)

        if used_pro_tsa:
            # Paid tier: Celebrate legal validity
            balance = self.settings_manager.get_last_credit_balance()
            message = f"""
<h3 style="color: {Colors.SUCCESS};">Firmados {signed_count} documento(s) con validez legal</h3>

<p style="margin-top: 15px;"><b>Tus documentos tienen:</b></p>
<ul style="line-height: 1.8; color: {Colors.TEXT_PRIMARY};">
    <li>✓ Hash registrado y verificable en selladomx.com</li>
    <li>✓ Sello de tiempo certificado RFC 3161</li>
    <li>✓ Fecha verificable por terceros confiables</li>
    <li>✓ Evidencia admisible en procesos legales</li>
</ul>

<p style="margin-top: 15px; padding: 12px; background: {Colors.PRIMARY_SUBTLE}; border-radius: 8px; color: {Colors.PRIMARY_ACTIVE};">
<b>💳 Créditos restantes:</b> {balance}
</p>
            """
            dialog.setText(message)
            dialog.setTextFormat(Qt.RichText)
            dialog.addButton("Entendido", QMessageBox.AcceptRole)

        else:
            # Free tier: Soft upsell
            message = f"""
<h3 style="color: {Colors.PRIMARY};">Firmados {signed_count} documento(s)</h3>

<p style="color: {Colors.WARNING}; margin-top: 10px; font-weight: 500;">
⚠️ Documentos firmados con TSA Gratuito (validez limitada, sin registro de hash).
</p>

<div style="background: {Colors.WARNING_LIGHT}; padding: 16px; border-radius: 12px; margin-top: 15px; border: 2px solid {Colors.WARNING_BORDER};">
<p style="margin: 0; font-weight: 600; color: {Colors.WARNING_DARK};">💡 ¿Necesitas validez legal garantizada?</p>
<p style="margin: 8px 0 0 0; color: {Colors.WARNING_DARK}; line-height: 1.6;">
TSA Profesional te da registro de hash verificable, certificación oficial RFC 3161 y fecha verificable por terceros por solo {CREDIT_PRICE_DISPLAY} por documento.
<br/><b>Ideal para:</b> Contratos, facturas, actas, y cualquier documento legal o empresarial.
</p>
</div>
            """
            dialog.setText(message)
            dialog.setTextFormat(Qt.RichText)

            btn_upgrade = dialog.addButton("Ver TSA Profesional", QMessageBox.ActionRole)
            btn_ok = dialog.addButton("Entendido", QMessageBox.AcceptRole)

            dialog.exec()

            # Handle upgrade click
            if dialog.clickedButton() == btn_upgrade:
                self._show_upgrade_benefits_dialog()
            return

        dialog.exec()

    def _on_tsa_credits_label_clicked(self):
        """Handle click on TSA credits label."""
        # Show benefits dialog if they don't have token or are out of credits
        if not self.settings_manager.has_api_key() or self.settings_manager.get_last_credit_balance() == 0:
            self._show_upgrade_benefits_dialog()

    def _on_buy_credits(self):
        """Open buy credits URL in browser."""
        webbrowser.open(BUY_CREDITS_URL)

    def _on_tsa_preference_changed(self, state):
        """Handle TSA preference checkbox change."""
        enabled = state == Qt.Checked.value
        self.settings_manager.set_use_professional_tsa(enabled)

        if enabled and self.settings_manager.get_last_credit_balance() == 0:
            # Show persuasive message with action buttons
            dialog = QMessageBox(self)
            dialog.setWindowTitle("🔒 Activa TSA Profesional")
            dialog.setIcon(QMessageBox.Information)

            message = f"""
<h3 style="color: {Colors.PRIMARY};">Necesitas créditos para TSA Profesional</h3>

<p>Para usar <b>TSA Profesional</b> y obtener validez legal garantizada,
necesitas tener créditos disponibles.</p>

<p style="margin-top: 15px;"><b>Beneficios del TSA Profesional:</b></p>
<ul style="margin-left: 20px; color: {Colors.SUCCESS};">
    <li>✓ Validez legal certificada</li>
    <li>✓ Cumplimiento NOM-151-SCFI-2016</li>
    <li>✓ Evidencia admisible en juicios</li>
    <li>✓ Solo {CREDIT_PRICE_DISPLAY} por documento</li>
</ul>

<p style="margin-top: 15px;">¿Deseas comprar créditos ahora?</p>
            """

            dialog.setText(message)
            dialog.setTextFormat(Qt.RichText)

            # Add custom buttons
            btn_buy = dialog.addButton("Comprar Créditos", QMessageBox.AcceptRole)
            btn_later = dialog.addButton("Después", QMessageBox.RejectRole)

            dialog.exec()

            if dialog.clickedButton() == btn_buy:
                webbrowser.open(BUY_CREDITS_URL)
            else:
                # Uncheck the box if they don't want to buy
                self.chk_professional_tsa.setChecked(False)

    def _refresh_balance_async(self):
        """Refresh credit balance in background."""
        if not self.settings_manager.has_api_key():
            return

        api_key = self.settings_manager.get_api_key()
        if not api_key:
            return

        self._balance_worker = ApiTestWorker(api_key, self.settings_manager, self)
        self._balance_worker.test_result.connect(self._on_balance_refreshed)
        self._balance_worker.start()

    def _on_balance_refreshed(self, success: bool, response: dict, error_msg: str):
        """Handle balance refresh result.

        Args:
            success: Whether refresh was successful
            response: Full balance response dict
            error_msg: Error message if failed
        """
        if success:
            credits = response.get("credits_remaining", 0)
            self.settings_manager.set_last_credit_balance(credits)

            # Update token metadata
            if "token_info" in response:
                self.settings_manager.set_token_info(response["token_info"])

            self._update_credit_label()
            self._update_tsa_credits_label()
            logger.info(f"Balance refreshed: {credits} credits")
        else:
            # Handle token expiration/revocation
            if "expired" in error_msg.lower() or "revoked" in error_msg.lower():
                QMessageBox.warning(
                    self,
                    "Token Inv\u00e1lido",
                    f"Tu token ha expirado o sido revocado.\n\n"
                    f"\u00bfDeseas configurar un nuevo token?",
                    QMessageBox.Yes | QMessageBox.No
                )
                # User will need to reconfigure manually
            else:
                logger.warning(f"Balance refresh failed: {error_msg}")

    # ========================================================================
    # Step 1 Methods
    # ========================================================================

    def _on_add_files(self):
        """Add PDF files to the list."""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Seleccionar archivos PDF",
            "",
            "Archivos PDF (*.pdf)"
        )

        for file_path in files:
            self.list_pdfs.addItem(file_path)

        if files:
            self._log_status(f"{len(files)} archivo(s) agregado(s)")
            self._check_step1_completion()
            self._update_credit_estimate()

    def _on_clear_files(self):
        """Clear PDF list."""
        self.list_pdfs.clear()
        self._log_status("Lista de archivos limpiada")
        self._check_step1_completion()
        self._update_credit_estimate()

    def _on_browse_output(self):
        """Browse for output directory."""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Seleccionar carpeta de destino para PDFs firmados",
            "",
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )

        if directory:
            self.output_dir = Path(directory)
            self.line_output_dir.setText(directory)
            self._log_status(f"Carpeta de destino: {directory}")
        else:
            # Clear if canceled
            self.output_dir = None
            self.line_output_dir.clear()

    def _check_step1_completion(self):
        """Check if step 1 is completed."""
        if self.list_pdfs.count() > 0:
            if self.step1.state != StepState.COMPLETED:
                self.step1.mark_completed()
                self._log_status("\u2713 Paso 1 completado: PDFs seleccionados", "green")
        else:
            if self.step1.state == StepState.COMPLETED:
                self.step1.state = StepState.ACTIVE

    def _on_step1_completed(self):
        """Handle step 1 completion."""
        # Activate step 2
        self.step2.activate()

    # ========================================================================
    # Step 2 Methods
    # ========================================================================

    def _on_browse_cert(self):
        """Select certificate file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar certificado",
            "",
            "Certificados (*.cer *.pem *.crt);;Todos los archivos (*)"
        )

        if file_path:
            self.line_cert_path.setText(file_path)
            self.settings_manager.set_last_cert_path(file_path)
            self._check_step2_fields()

    def _on_browse_key(self):
        """Select private key file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar clave privada",
            "",
            "Claves privadas (*.key *.pem);;Todos los archivos (*)"
        )

        if file_path:
            self.line_key_path.setText(file_path)
            self.settings_manager.set_last_key_path(file_path)
            self._check_step2_fields()

    def _check_step2_fields(self):
        """Check if all step 2 fields are filled (but don't validate yet)."""
        cert_path = self.line_cert_path.text()
        key_path = self.line_key_path.text()
        password = self.line_password.text()

        if all([cert_path, key_path, password]):
            # All fields filled - mark step 2 as completed
            self.label_cert_status.setText("Listo para firmar")
            self.label_cert_status.setStyleSheet(f"color: {Colors.INFO}; font-weight: {Typography.WEIGHT_MEDIUM};")

            # Mark step 2 as completed (will trigger _on_step2_completed)
            if self.step2.state != StepState.COMPLETED:
                logger.info("Marking step 2 as completed (all fields filled)")
                self.step2.mark_completed()
        else:
            # Some fields empty - reset if it was completed
            self.label_cert_status.setText("Complete todos los campos")
            self.label_cert_status.setStyleSheet(f"color: {Colors.TEXT_TERTIARY};")

            if self.step2.state == StepState.COMPLETED:
                self.step2.state = StepState.ACTIVE
                self.step3.state = StepState.DISABLED
                self.btn_sign.setEnabled(False)

    def _validate_certificate(self):
        """Validate certificate and private key.

        Returns:
            bool: True if validation successful, False otherwise
        """
        cert_path = self.line_cert_path.text()
        key_path = self.line_key_path.text()
        password = self.line_password.text()

        # Check all fields are filled
        if not all([cert_path, key_path, password]):
            self.label_cert_status.setText("Complete todos los campos")
            self.label_cert_status.setProperty("class", "secondary")
            self.label_cert_status.setStyleSheet(f"color: {Colors.ERROR};")
            self.cert = None
            self.private_key = None
            QMessageBox.warning(
                self,
                "Campos incompletos",
                "Por favor complete todos los campos:\n"
                "- Certificado (.cer)\n"
                "- Clave privada (.key)\n"
                "- Contrase\u00f1a"
            )
            return False

        try:
            # Validate certificate
            validator = CertificateValidator(
                Path(cert_path),
                Path(key_path),
                password
            )

            self.cert, self.private_key = validator.validate_all()

            # Get certificate info
            cert_info = validator.get_certificate_info(self.cert)
            cn = cert_info.get('common_name', 'Desconocido')
            expiry = cert_info['not_after'][:10]

            self.label_cert_status.setText(
                f"\u2713 Certificado v\u00e1lido: {cn} (Expira: {expiry})"
            )
            self.label_cert_status.setProperty("class", "success")
            self.label_cert_status.setStyleSheet(f"color: {Colors.SUCCESS}; font-weight: {Typography.WEIGHT_MEDIUM};")
            self._log_status(f"\u2713 Certificado validado: {cn}", Colors.SUCCESS)

            return True

        except CertificateExpiredError as e:
            self._show_cert_error(f"Certificado expirado: {e}")
            return False
        except CertificateRevokedError as e:
            self._show_cert_error(f"Certificado revocado: {e}")
            return False
        except CertificateError as e:
            self._show_cert_error(str(e))
            return False
        except Exception as e:
            self._show_cert_error(f"Error: {e}")
            return False

    def _show_cert_error(self, message: str):
        """Show certificate error."""
        self.label_cert_status.setText(f"\u2717 {message}")
        self.label_cert_status.setProperty("class", "error")
        self.label_cert_status.setStyleSheet(f"color: {Colors.ERROR}; font-weight: {Typography.WEIGHT_MEDIUM};")
        self.cert = None
        self.private_key = None
        self._log_status(f"Error de certificado: {message}", Colors.ERROR)

        if self.step2.state == StepState.COMPLETED:
            self.step2.state = StepState.ACTIVE
            self.step3.state = StepState.DISABLED

    def _on_step2_completed(self):
        """Handle step 2 completion."""
        logger.info("Step 2 completed - activating step 3")
        # Activate step 3
        self.step3.activate()
        self.btn_sign.setEnabled(True)
        self._log_status("\u2713 Paso 2 completado: Listo para firmar", Colors.SUCCESS)

    # ========================================================================
    # Step 3 Methods
    # ========================================================================

    def _on_sign_clicked(self):
        """Start signing process."""
        # First, validate certificate if not already validated
        if not self.cert or not self.private_key:
            self._log_status("Validando certificado...", Colors.INFO)
            if not self._validate_certificate():
                # Validation failed, error already shown
                return

        # Get PDF list
        pdf_paths = []
        for i in range(self.list_pdfs.count()):
            pdf_paths.append(Path(self.list_pdfs.item(i).text()))

        if not pdf_paths:
            return

        # Check professional TSA settings
        use_professional_tsa = self.chk_professional_tsa.isChecked()
        api_key = None
        signer_cn = ""
        signer_serial = ""

        if use_professional_tsa:
            api_key = self.settings_manager.get_api_key()
            if not api_key:
                QMessageBox.warning(
                    self,
                    "API Key requerida",
                    "Para usar TSA profesional necesitas configurar tu API key.\n\n"
                    "Puedes configurarla desde el bot\u00f3n 'Configurar API Key'."
                )
                return

            balance = self.settings_manager.get_last_credit_balance()
            if balance < len(pdf_paths):
                reply = QMessageBox.question(
                    self,
                    "Cr\u00e9ditos insuficientes",
                    f"Tienes {balance} cr\u00e9dito(s) pero vas a firmar {len(pdf_paths)} archivo(s).\n\n"
                    "Los archivos sin cr\u00e9ditos se firmar\u00e1n con TSA gratuito.\n\n"
                    "\u00bfDeseas continuar?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes,
                )
                if reply == QMessageBox.No:
                    return

            # Extract CN and serial from certificate
            try:
                from cryptography.x509 import NameOID
                cn_attrs = self.cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)
                signer_cn = cn_attrs[0].value if cn_attrs else ""
                signer_serial = format(self.cert.serial_number, 'x')
            except Exception:
                pass

        self._used_professional_tsa = use_professional_tsa

        # Disable UI
        self._set_ui_enabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(len(pdf_paths))
        self.progress_bar.setValue(0)
        self.text_status.clear()

        self._log_status(f"Iniciando firma de {len(pdf_paths)} archivo(s)...")
        if use_professional_tsa:
            self._log_status("TSA profesional activado", Colors.INFO)

        # Create and configure worker
        tsa_client = TSAClient()
        self.signing_worker = SigningWorker(
            pdf_paths,
            self.cert,
            self.private_key,
            tsa_client,
            self.output_dir,
            use_professional_tsa=use_professional_tsa,
            api_key=api_key,
            signer_cn=signer_cn,
            signer_serial=signer_serial,
        )

        self.signing_worker.progress.connect(self._on_progress)
        self.signing_worker.file_completed.connect(self._on_file_completed)
        self.signing_worker.finished.connect(self._on_signing_finished)

        # Start signing
        self.signing_worker.start()

    def _on_progress(self, current: int, total: int):
        """Update progress bar."""
        self.progress_bar.setValue(current)
        self._log_status(f"Procesando archivo {current}/{total}...")

    def _on_file_completed(self, filename: str, success: bool, message: str, verification_url: str = ""):
        """Handle file completion."""
        status = "\u2713" if success else "\u2717"
        color = Colors.SUCCESS if success else Colors.ERROR

        if verification_url:
            self._log_status(
                f'{status} {filename}: {message} '
                f'- <a href="{verification_url}">Ver certificado</a>',
                color,
            )
        else:
            self._log_status(f"{status} {filename}: {message}", color)

    def _on_signing_finished(self, errors: List[str]):
        """Handle signing completion."""
        self.progress_bar.setVisible(False)
        self._set_ui_enabled(True)

        # Show summary
        total = self.list_pdfs.count()
        success_count = total - len(errors)

        # Check for credit-related errors
        has_credit_errors = any("cr\u00e9ditos" in e.lower() for e in errors)

        if errors:
            QMessageBox.warning(
                self,
                "Firma completada con errores",
                f"Se firmaron {success_count} de {total} archivos.\n\n"
                f"Errores:\n" + "\n".join(errors[:5]) +
                (f"\n... y {len(errors) - 5} m\u00e1s" if len(errors) > 5 else "")
            )
        else:
            # Show enhanced success dialog with conversion optimization
            self._show_signing_success_dialog(success_count, self._used_professional_tsa)

        self._log_status(f"Proceso completado: {success_count}/{total} exitosos")

        # Refresh balance if professional TSA was used
        if self._used_professional_tsa:
            self._refresh_balance_async()

        # Offer to buy credits if needed
        if has_credit_errors:
            reply = QMessageBox.question(
                self,
                "Comprar cr\u00e9ditos",
                "Algunos archivos no pudieron registrarse con TSA profesional "
                "por falta de cr\u00e9ditos.\n\n"
                "\u00bfDeseas comprar m\u00e1s cr\u00e9ditos?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes,
            )
            if reply == QMessageBox.Yes:
                webbrowser.open(BUY_CREDITS_URL)

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _set_ui_enabled(self, enabled: bool):
        """Enable/disable UI controls."""
        self.btn_add_files.setEnabled(enabled)
        self.btn_clear_files.setEnabled(enabled)
        self.btn_browse_output.setEnabled(enabled)
        self.btn_browse_cert.setEnabled(enabled)
        self.btn_browse_key.setEnabled(enabled)
        self.line_password.setEnabled(enabled)
        self.btn_settings.setEnabled(enabled)
        self.btn_buy_credits.setEnabled(enabled)
        self.chk_professional_tsa.setEnabled(
            enabled and self.settings_manager.has_api_key()
        )
        self.btn_sign.setEnabled(
            enabled and
            self.cert is not None and
            self.step3.state == StepState.ACTIVE
        )

    def _log_status(self, message: str, color: str = "black"):
        """Add message to status log."""
        self.text_status.append(f'<span style="color: {color};">{message}</span>')
        logger.info(message)

    def closeEvent(self, event):
        """Clean sensitive data on close."""
        if hasattr(self, 'private_key'):
            del self.private_key
        if hasattr(self, 'cert'):
            del self.cert
        self.line_password.clear()

        logger.info("RedesignedMainView closed, sensitive data cleared")
        event.accept()
