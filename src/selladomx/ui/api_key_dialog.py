"""API Key configuration dialog."""
import logging
import re
from typing import Optional

from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QWidget,
    QMessageBox,
)

from ..api.client import SelladoMXAPIClient
from ..api.exceptions import AuthenticationError, NetworkError, APIError
from .design_tokens import Colors, Typography, Spacing, BorderRadius, ComponentSizes

logger = logging.getLogger(__name__)

# Accept both old format (64 hex chars) and new format (smx_xxxxx)
TOKEN_PATTERN = re.compile(r"^(smx_[0-9a-f]{5,}|[0-9a-fA-F]{64})$")


class ApiTestWorker(QThread):
    """Worker thread to test API connection without blocking UI."""

    test_result = Signal(bool, dict, str)  # success, response_dict, error_msg

    def __init__(self, api_key: str, settings_manager, parent=None):
        super().__init__(parent)
        self.api_key = api_key
        self.settings_manager = settings_manager

    def run(self):
        try:
            client = SelladoMXAPIClient(api_key=self.api_key)
            response = client.get_balance()  # Now returns full dict

            # Store token metadata in settings
            if "token_info" in response:
                self.settings_manager.set_token_info(response["token_info"])
                self.settings_manager.set_last_credit_balance(response["credits_remaining"])

            self.test_result.emit(True, response, "")
        except AuthenticationError as e:
            self.test_result.emit(False, {}, f"Token inv\u00e1lido: {e.message}")
        except NetworkError as e:
            self.test_result.emit(False, {}, f"Error de red: {e.message}")
        except APIError as e:
            self.test_result.emit(False, {}, f"Error del servidor: {e.message}")
        except Exception as e:
            self.test_result.emit(False, {}, f"Error inesperado: {e}")


class ApiKeyDialog(QDialog):
    """Dialog for configuring the SelladoMX API key."""

    def __init__(self, settings_manager, parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self._test_worker: Optional[ApiTestWorker] = None
        self._test_success = False
        self._test_response = {}

        self.setWindowTitle("Configurar Token de Autenticación")
        self.setModal(True)
        self.setFixedSize(500, 450)

        self._setup_ui()
        self._connect_signals()
        self._load_existing_key()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Content area
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(Spacing.XXXL, Spacing.XXXL, Spacing.XXXL, Spacing.XL)
        content_layout.setSpacing(Spacing.LG)

        # Title
        title = QLabel("Configurar Token de Autenticación")
        title.setStyleSheet(
            f"font-size: {Typography.FONT_2XL}px; "
            f"font-weight: {Typography.WEIGHT_SEMIBOLD}; "
            f"color: {Colors.TEXT_PRIMARY};"
        )
        content_layout.addWidget(title)

        # Subtitle
        subtitle = QLabel(
            "Ingresa tu token de SelladoMX para acceder a TSA profesional.\n"
            "Formato esperado: smx_xxxxxxxxxxxxx"
        )
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet(
            f"font-size: {Typography.FONT_BASE}px; "
            f"color: {Colors.TEXT_SECONDARY}; "
            f"line-height: {Typography.LINE_HEIGHT_NORMAL};"
        )
        content_layout.addWidget(subtitle)

        # API Key input
        self.line_api_key = QLineEdit()
        self.line_api_key.setPlaceholderText("Pega tu token aquí (smx_xxxxx...)")
        self.line_api_key.setMaxLength(100)  # Allow longer tokens
        self.line_api_key.setStyleSheet(
            f"QLineEdit {{"
            f"font-family: 'Menlo', 'Consolas', 'Monaco', 'Courier New', monospace; "
            f"font-size: {Typography.FONT_SM}px; "
            f"padding: {Spacing.MD}px;"
            f"}}"
        )
        content_layout.addWidget(self.line_api_key)

        # Format validation label
        self.label_format = QLabel("")
        self.label_format.setStyleSheet(
            f"font-size: {Typography.FONT_SM}px; "
            f"color: {Colors.TEXT_SECONDARY};"
        )
        content_layout.addWidget(self.label_format)

        # Test result label (hidden by default)
        self.label_result = QLabel("")
        self.label_result.setWordWrap(True)
        self.label_result.setVisible(False)
        self.label_result.setStyleSheet(
            f"font-size: {Typography.FONT_BASE}px; "
            f"padding: {Spacing.MD}px; "
            f"border-radius: {BorderRadius.MD}px;"
        )
        content_layout.addWidget(self.label_result)

        # Token info display area (initially hidden)
        self.label_token_info = QLabel("")
        self.label_token_info.setWordWrap(True)
        self.label_token_info.setVisible(False)
        self.label_token_info.setStyleSheet(
            f"font-size: {Typography.FONT_SM}px; "
            f"color: {Colors.TEXT_SECONDARY}; "
            f"padding: {Spacing.MD}px;"
        )
        content_layout.addWidget(self.label_token_info)

        content_layout.addStretch()
        layout.addWidget(content)

        # Navigation bar
        nav_widget = QWidget()
        nav_widget.setStyleSheet(
            f"QWidget {{"
            f"background-color: {Colors.BG_SECONDARY}; "
            f"border-top: 1px solid {Colors.BORDER_DEFAULT};"
            f"}}"
        )
        nav_layout = QHBoxLayout(nav_widget)
        nav_layout.setContentsMargins(Spacing.XL, Spacing.LG, Spacing.XL, Spacing.LG)
        nav_layout.setSpacing(Spacing.MD)

        # Delete Token button (danger, only visible if key exists)
        self.btn_delete = QPushButton("Borrar Token")
        self.btn_delete.setMinimumHeight(ComponentSizes.BUTTON_MD)
        self.btn_delete.setStyleSheet(
            f"QPushButton {{"
            f"background-color: {Colors.ERROR}; "
            f"color: {Colors.TEXT_PRIMARY}; "
            f"border: none; "
            f"border-radius: {BorderRadius.LG}px; "
            f"padding: 0 {Spacing.LG}px; "
            f"font-size: {Typography.FONT_BASE}px; "
            f"font-weight: {Typography.WEIGHT_MEDIUM};"
            f"}}"
            f"QPushButton:hover {{ background-color: {Colors.ERROR_HOVER}; }}"
            f"QPushButton:pressed {{ background-color: {Colors.ERROR_ACTIVE}; }}"
        )
        self.btn_delete.setVisible(False)
        nav_layout.addWidget(self.btn_delete)

        nav_layout.addStretch()

        # Test connection button
        self.btn_test = QPushButton("Probar conexi\u00f3n")
        self.btn_test.setEnabled(False)
        self.btn_test.setMinimumWidth(140)
        self.btn_test.setMinimumHeight(ComponentSizes.BUTTON_MD)
        self.btn_test.setStyleSheet(
            f"QPushButton {{"
            f"background-color: {Colors.SURFACE_DEFAULT}; "
            f"color: {Colors.TEXT_PRIMARY}; "
            f"border: 1px solid {Colors.BORDER_DEFAULT}; "
            f"border-radius: {BorderRadius.LG}px; "
            f"padding: 0 {Spacing.LG}px; "
            f"font-size: {Typography.FONT_BASE}px;"
            f"}}"
            f"QPushButton:hover {{ background-color: {Colors.BG_HOVER}; }}"
            f"QPushButton:disabled {{"
            f"background-color: {Colors.BG_SECONDARY}; "
            f"color: {Colors.TEXT_DISABLED}; "
            f"border-color: {Colors.BORDER_SUBTLE};"
            f"}}"
        )
        nav_layout.addWidget(self.btn_test)

        # Save button
        self.btn_save = QPushButton("Guardar")
        self.btn_save.setEnabled(False)
        self.btn_save.setMinimumWidth(100)
        self.btn_save.setMinimumHeight(ComponentSizes.BUTTON_MD)
        self.btn_save.setStyleSheet(
            f"QPushButton {{"
            f"background-color: {Colors.SUCCESS}; "
            f"color: {Colors.TEXT_PRIMARY}; "
            f"border: none; "
            f"border-radius: {BorderRadius.LG}px; "
            f"padding: 0 {Spacing.LG}px; "
            f"font-size: {Typography.FONT_BASE}px; "
            f"font-weight: {Typography.WEIGHT_SEMIBOLD};"
            f"}}"
            f"QPushButton:hover {{ background-color: {Colors.PRIMARY_LIGHT}; }}"
            f"QPushButton:pressed {{ background-color: {Colors.PRIMARY_HOVER}; }}"
            f"QPushButton:disabled {{"
            f"background-color: {Colors.BORDER_SUBTLE}; "
            f"color: {Colors.TEXT_DISABLED};"
            f"}}"
        )
        nav_layout.addWidget(self.btn_save)

        # Cancel button
        self.btn_cancel = QPushButton("Cancelar")
        self.btn_cancel.setMinimumWidth(100)
        self.btn_cancel.setMinimumHeight(ComponentSizes.BUTTON_MD)
        self.btn_cancel.setStyleSheet(
            f"QPushButton {{"
            f"background-color: {Colors.SURFACE_DEFAULT}; "
            f"color: {Colors.TEXT_PRIMARY}; "
            f"border: 1px solid {Colors.BORDER_DEFAULT}; "
            f"border-radius: {BorderRadius.LG}px; "
            f"padding: 0 {Spacing.LG}px; "
            f"font-size: {Typography.FONT_BASE}px;"
            f"}}"
            f"QPushButton:hover {{ background-color: {Colors.BG_HOVER}; }}"
        )
        nav_layout.addWidget(self.btn_cancel)

        layout.addWidget(nav_widget)

    def _connect_signals(self):
        self.line_api_key.textChanged.connect(self._on_key_changed)
        self.btn_test.clicked.connect(self._on_test_clicked)
        self.btn_save.clicked.connect(self._on_save_clicked)
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_delete.clicked.connect(self._on_delete_clicked)

    def _load_existing_key(self):
        if self.settings_manager.has_api_key():
            api_key = self.settings_manager.get_api_key()
            if api_key:
                self.line_api_key.setText(api_key)
            self.btn_delete.setVisible(True)

    def _on_key_changed(self, text: str):
        self._test_success = False
        self.btn_save.setEnabled(False)
        self.label_result.setVisible(False)
        self.label_token_info.setVisible(False)

        if not text:
            self.label_format.setText("")
            self.btn_test.setEnabled(False)
            return

        if TOKEN_PATTERN.match(text):
            self.label_format.setText("✓ Formato válido")
            self.label_format.setStyleSheet(
                f"font-size: {Typography.FONT_SM}px; "
                f"color: {Colors.SUCCESS};"
            )
            self.btn_test.setEnabled(True)
        else:
            self.label_format.setText("✗ Formato inválido (debe ser smx_xxxxx...)")
            self.label_format.setStyleSheet(
                f"font-size: {Typography.FONT_SM}px; "
                f"color: {Colors.ERROR};"
            )
            self.btn_test.setEnabled(False)

    def _on_test_clicked(self):
        api_key = self.line_api_key.text().strip()
        if not TOKEN_PATTERN.match(api_key):
            return

        self.btn_test.setEnabled(False)
        self.btn_test.setText("Probando...")
        self.label_result.setVisible(True)
        self.label_result.setText("Conectando al servidor...")
        self.label_result.setStyleSheet(
            f"font-size: {Typography.FONT_BASE}px; "
            f"color: {Colors.INFO}; "
            f"background-color: {Colors.STEP_ACTIVE_BG}; "
            f"padding: {Spacing.MD}px; "
            f"border-radius: {BorderRadius.MD}px;"
        )

        self._test_worker = ApiTestWorker(api_key, self.settings_manager, self)
        self._test_worker.test_result.connect(self._on_test_result)
        self._test_worker.start()

    def _on_test_result(self, success: bool, response: dict, error_msg: str):
        self.btn_test.setEnabled(True)
        self.btn_test.setText("Probar conexi\u00f3n")
        self.label_result.setVisible(True)

        if success:
            self._test_success = True
            self._test_response = response

            credits = response.get("credits_remaining", 0)
            email = response.get("email", "N/A")
            token_info = response.get("token_info", {})

            # Show success with token metadata
            self.label_result.setText(
                f"✅ Conexi\u00f3n exitosa\n"
                f"Email: {email}\n"
                f"Cr\u00e9ditos disponibles: {credits}"
            )
            self.label_result.setStyleSheet(
                f"font-size: {Typography.FONT_BASE}px; "
                f"color: {Colors.SUCCESS}; "
                f"background-color: {Colors.STEP_COMPLETED_BG}; "
                f"padding: {Spacing.MD}px; "
                f"border-radius: {BorderRadius.MD}px;"
            )

            # Show token info
            if token_info:
                is_primary = token_info.get("is_primary", False)
                alias = token_info.get("alias")
                expires_at = token_info.get("expires_at")

                info_text = f"\nTipo: {'Token Primario' if is_primary else 'Token Derivado'}"
                if alias:
                    info_text += f"\nNombre: {alias}"
                if expires_at:
                    info_text += f"\nExpira: {expires_at}"

                self.label_token_info.setText(info_text)
                self.label_token_info.setVisible(True)

            self.btn_save.setEnabled(True)
        else:
            self._test_success = False
            self.label_result.setText(f"❌ Error: {error_msg}")
            self.label_result.setStyleSheet(
                f"font-size: {Typography.FONT_BASE}px; "
                f"color: {Colors.ERROR}; "
                f"background-color: {Colors.STEP_DISABLED_BG}; "
                f"padding: {Spacing.MD}px; "
                f"border-radius: {BorderRadius.MD}px;"
            )
            self.label_token_info.setVisible(False)
            self.btn_save.setEnabled(False)

    def _on_save_clicked(self):
        if not self._test_success:
            return

        token = self.line_api_key.text().strip()

        # Save token
        self.settings_manager.set_token(token)

        # Token metadata is already saved by ApiTestWorker during test
        # Just update balance in case it changed
        if self._test_response:
            self.settings_manager.set_last_credit_balance(
                self._test_response.get("credits_remaining", 0)
            )

        QMessageBox.information(
            self,
            "Token guardado",
            "El token se ha guardado correctamente."
        )
        logger.info("Token saved successfully")
        self.accept()

    def _on_delete_clicked(self):
        reply = QMessageBox.question(
            self,
            "Borrar Token",
            "Se borrar\u00e1 tu token y se desactivar\u00e1 el TSA profesional.\n\n"
            "\u00bfEst\u00e1s seguro?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.settings_manager.clear_token()
            self.settings_manager.set_use_professional_tsa(False)
            logger.info("Token deleted")
            self.accept()
