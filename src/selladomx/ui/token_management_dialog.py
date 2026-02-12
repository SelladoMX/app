"""Comprehensive token management interface."""
import logging
from typing import Optional

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QTabWidget, QWidget,
    QLineEdit, QComboBox, QSpinBox, QTextEdit, QMessageBox,
    QHeaderView, QApplication
)
from PySide6.QtCore import Qt, Signal, QThread

from ..utils.settings_manager import SettingsManager
from ..api.client import SelladoMXAPIClient
from ..api.exceptions import APIError, PrimaryTokenRequiredError
from .design_tokens import Colors, Typography, Spacing, BorderRadius, ComponentSizes

logger = logging.getLogger(__name__)


# Worker threads
class TokenListWorker(QThread):
    """Worker to load token list."""
    list_result = Signal(bool, dict, str)  # success, tokens, error

    def __init__(self, token: str):
        super().__init__()
        self.token = token

    def run(self):
        try:
            client = SelladoMXAPIClient(api_key=self.token)
            tokens = client.list_tokens()
            self.list_result.emit(True, tokens, "")
        except APIError as e:
            self.list_result.emit(False, {}, e.message)


class TokenDeriveWorker(QThread):
    """Worker to generate derived token."""
    derive_result = Signal(bool, str, dict, str)  # success, token, metadata, error

    def __init__(self, primary_token: str, alias: str, expires_in_days: Optional[int] = None):
        super().__init__()
        self.primary_token = primary_token
        self.alias = alias
        self.expires_in_days = expires_in_days

    def run(self):
        try:
            client = SelladoMXAPIClient(api_key=self.primary_token)
            result = client.derive_token(self.alias, self.expires_in_days)
            token = result.get("token", "")
            self.derive_result.emit(True, token, result, "")
        except PrimaryTokenRequiredError:
            self.derive_result.emit(False, "", {}, "Solo los tokens primarios pueden generar tokens derivados")
        except APIError as e:
            self.derive_result.emit(False, "", {}, e.message)


class TokenRevokeWorker(QThread):
    """Worker to revoke token."""
    revoke_result = Signal(bool, str, str)  # success, token_id, error

    def __init__(self, auth_token: str, token_id: str):
        super().__init__()
        self.auth_token = auth_token
        self.token_id = token_id

    def run(self):
        try:
            client = SelladoMXAPIClient(api_key=self.auth_token)
            client.revoke_token(self.token_id)
            self.revoke_result.emit(True, self.token_id, "")
        except APIError as e:
            self.revoke_result.emit(False, self.token_id, e.message)


class TokenManagementDialog(QDialog):
    """Comprehensive token management interface."""

    def __init__(self, settings_manager: SettingsManager, parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.token = settings_manager.get_token()
        self.token_list_cache = None
        self._generated_token = ""

        self.setWindowTitle("Administrar Tokens")
        self.setModal(True)
        self.setMinimumSize(700, 500)

        self._setup_ui()
        self._connect_signals()

        # Load tokens on open
        self._refresh_token_list()

    def _setup_ui(self):
        """Set up the UI with tabs for different functions."""
        layout = QVBoxLayout(self)

        # Tab widget
        self.tabs = QTabWidget()

        # Tab 1: List tokens
        self.tab_list = self._create_list_tab()
        self.tabs.addTab(self.tab_list, "Mis Tokens")

        # Tab 2: Create derived token (only if primary)
        token_info = self.settings_manager.get_token_info()
        if token_info.get("is_primary", False):
            self.tab_create = self._create_derive_tab()
            self.tabs.addTab(self.tab_create, "Generar Token de Equipo")

        layout.addWidget(self.tabs)

        # Close button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.btn_close = QPushButton("Cerrar")
        btn_layout.addWidget(self.btn_close)
        layout.addLayout(btn_layout)

    def _create_list_tab(self) -> QWidget:
        """Create the token list tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Header with refresh button
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Tus tokens de autenticación"))
        header_layout.addStretch()
        self.btn_refresh = QPushButton("🔄 Actualizar")
        header_layout.addWidget(self.btn_refresh)
        layout.addLayout(header_layout)

        # Token table
        self.table_tokens = QTableWidget()
        self.table_tokens.setColumnCount(6)
        self.table_tokens.setHorizontalHeaderLabels([
            "Tipo", "Nombre", "Preview", "Creado", "Expira", "Acciones"
        ])
        self.table_tokens.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_tokens.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_tokens.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table_tokens)

        return widget

    def _create_derive_tab(self) -> QWidget:
        """Create the derive token tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Title
        title = QLabel("Generar Token de Equipo")
        title.setStyleSheet(
            f"font-size: {Typography.FONT_XL}px; "
            f"font-weight: {Typography.WEIGHT_SEMIBOLD};"
        )
        layout.addWidget(title)

        # Description
        desc = QLabel(
            "Los tokens de equipo comparten los mismos créditos de tu cuenta,\n"
            "pero pueden ser revocados individualmente."
        )
        desc.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
        layout.addWidget(desc)

        layout.addSpacing(Spacing.XL)

        # Alias input
        layout.addWidget(QLabel("Nombre del token (obligatorio):"))
        self.input_alias = QLineEdit()
        self.input_alias.setPlaceholderText("Ej: Laptop de Juan, PC de desarrollo...")
        self.input_alias.setMaxLength(50)
        layout.addWidget(self.input_alias)

        layout.addSpacing(Spacing.MD)

        # Expiration selector
        layout.addWidget(QLabel("Expiración (opcional):"))
        exp_layout = QHBoxLayout()
        self.combo_expiration = QComboBox()
        self.combo_expiration.addItems([
            "Sin expiración",
            "30 días",
            "90 días",
            "1 año",
            "Personalizado"
        ])
        exp_layout.addWidget(self.combo_expiration)

        self.spin_custom_days = QSpinBox()
        self.spin_custom_days.setRange(1, 3650)
        self.spin_custom_days.setValue(365)
        self.spin_custom_days.setSuffix(" días")
        self.spin_custom_days.setVisible(False)
        exp_layout.addWidget(self.spin_custom_days)

        exp_layout.addStretch()
        layout.addLayout(exp_layout)

        layout.addSpacing(Spacing.XL)

        # Generate button
        self.btn_generate = QPushButton("Generar Token")
        self.btn_generate.setStyleSheet(
            f"QPushButton {{"
            f"background-color: {Colors.SUCCESS}; "
            f"color: {Colors.TEXT_PRIMARY}; "
            f"border: none; "
            f"border-radius: {BorderRadius.LG}px; "
            f"padding: {Spacing.MD}px {Spacing.LG}px; "
            f"font-size: {Typography.FONT_BASE}px; "
            f"font-weight: {Typography.WEIGHT_SEMIBOLD};"
            f"}}"
            f"QPushButton:hover {{ background-color: {Colors.PRIMARY_LIGHT}; }}"
            f"QPushButton:disabled {{"
            f"background-color: {Colors.BORDER_SUBTLE}; "
            f"color: {Colors.TEXT_DISABLED};"
            f"}}"
        )
        self.btn_generate.setEnabled(False)
        layout.addWidget(self.btn_generate)

        # Result area (hidden initially)
        self.text_generated_token = QTextEdit()
        self.text_generated_token.setReadOnly(True)
        self.text_generated_token.setMaximumHeight(100)
        self.text_generated_token.setVisible(False)
        layout.addWidget(self.text_generated_token)

        self.btn_copy_token = QPushButton("📋 Copiar Token")
        self.btn_copy_token.setVisible(False)
        layout.addWidget(self.btn_copy_token)

        layout.addStretch()

        return widget

    def _connect_signals(self):
        """Connect signals to slots."""
        self.btn_close.clicked.connect(self.accept)
        self.btn_refresh.clicked.connect(self._refresh_token_list)

        # Create tab signals (if exists)
        if hasattr(self, 'tab_create'):
            self.input_alias.textChanged.connect(self._validate_derive_form)
            self.combo_expiration.currentTextChanged.connect(self._on_expiration_changed)
            self.btn_generate.clicked.connect(self._on_generate_clicked)
            self.btn_copy_token.clicked.connect(self._on_copy_token)

    def _validate_derive_form(self):
        """Enable generate button only if alias is provided."""
        alias = self.input_alias.text().strip()
        self.btn_generate.setEnabled(len(alias) > 0)

    def _on_expiration_changed(self, text: str):
        """Show/hide custom days input."""
        self.spin_custom_days.setVisible(text == "Personalizado")

    def _refresh_token_list(self):
        """Load token list from API."""
        self.btn_refresh.setEnabled(False)
        self.btn_refresh.setText("⏳ Cargando...")

        self.list_worker = TokenListWorker(self.token)
        self.list_worker.list_result.connect(self._on_tokens_loaded)
        self.list_worker.start()

    def _on_tokens_loaded(self, success: bool, tokens: dict, error_msg: str):
        """Handle token list result."""
        self.btn_refresh.setEnabled(True)
        self.btn_refresh.setText("🔄 Actualizar")

        if success:
            self.token_list_cache = tokens
            self._populate_token_table(tokens)
        else:
            QMessageBox.critical(
                self,
                "Error al cargar tokens",
                f"No se pudieron cargar los tokens:\n{error_msg}"
            )

    def _populate_token_table(self, tokens: dict):
        """Populate the token table with data."""
        self.table_tokens.setRowCount(0)

        # Add primary token
        primary = tokens.get("primary")
        if primary:
            self._add_token_row(primary, is_primary=True)

        # Add derived tokens
        for derived in tokens.get("derived", []):
            self._add_token_row(derived, is_primary=False)

    def _add_token_row(self, token_data: dict, is_primary: bool):
        """Add a token row to the table."""
        row = self.table_tokens.rowCount()
        self.table_tokens.insertRow(row)

        # Type
        type_label = "Primario" if is_primary else "Derivado"
        self.table_tokens.setItem(row, 0, QTableWidgetItem(type_label))

        # Name
        name = token_data.get("alias", "-")
        self.table_tokens.setItem(row, 1, QTableWidgetItem(name))

        # Preview
        preview = token_data.get("token_preview", "")
        self.table_tokens.setItem(row, 2, QTableWidgetItem(preview))

        # Created
        created = token_data.get("created_at", "")[:10]  # Just date
        self.table_tokens.setItem(row, 3, QTableWidgetItem(created))

        # Expires
        expires = token_data.get("expires_at", "Nunca")
        if expires and expires != "Nunca":
            expires = expires[:10]  # Just date
        self.table_tokens.setItem(row, 4, QTableWidgetItem(expires))

        # Actions (revoke button for derived tokens only)
        actions_widget = QWidget()
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setContentsMargins(Spacing.XS, Spacing.XS, Spacing.XS, Spacing.XS)

        if not is_primary:
            btn_revoke = QPushButton("Revocar")
            btn_revoke.setStyleSheet(
                f"QPushButton {{"
                f"background-color: {Colors.ERROR}; "
                f"color: {Colors.TEXT_PRIMARY}; "
                f"border: none; "
                f"border-radius: {BorderRadius.MD}px; "
                f"padding: {Spacing.XS}px {Spacing.MD}px; "
                f"font-size: {Typography.FONT_SM}px;"
                f"}}"
                f"QPushButton:hover {{ background-color: {Colors.ERROR_HOVER}; }}"
            )
            btn_revoke.clicked.connect(
                lambda: self._on_revoke_clicked(token_data.get("id"))
            )
            actions_layout.addWidget(btn_revoke)
        else:
            actions_layout.addWidget(QLabel("-"))

        self.table_tokens.setCellWidget(row, 5, actions_widget)

    def _on_generate_clicked(self):
        """Generate derived token."""
        alias = self.input_alias.text().strip()

        # Get expiration
        expires_in_days = None
        exp_text = self.combo_expiration.currentText()
        if exp_text == "30 días":
            expires_in_days = 30
        elif exp_text == "90 días":
            expires_in_days = 90
        elif exp_text == "1 año":
            expires_in_days = 365
        elif exp_text == "Personalizado":
            expires_in_days = self.spin_custom_days.value()

        # Disable UI
        self.btn_generate.setEnabled(False)
        self.btn_generate.setText("⏳ Generando...")

        # Start worker
        self.derive_worker = TokenDeriveWorker(self.token, alias, expires_in_days)
        self.derive_worker.derive_result.connect(self._on_token_generated)
        self.derive_worker.start()

    def _on_token_generated(self, success: bool, token: str, metadata: dict, error_msg: str):
        """Handle token generation result."""
        self.btn_generate.setEnabled(True)
        self.btn_generate.setText("Generar Token")

        if success:
            # Show generated token
            self.text_generated_token.setText(
                f"✅ Token generado exitosamente:\n\n{token}\n\n"
                f"⚠️ Guarda este token. No volverá a mostrarse completo."
            )
            self.text_generated_token.setVisible(True)
            self.btn_copy_token.setVisible(True)

            # Store token for copy
            self._generated_token = token

            # Clear form
            self.input_alias.clear()

            # Refresh list
            self._refresh_token_list()
        else:
            QMessageBox.critical(
                self,
                "Error al generar token",
                f"No se pudo generar el token:\n{error_msg}"
            )

    def _on_copy_token(self):
        """Copy generated token to clipboard."""
        clipboard = QApplication.clipboard()
        clipboard.setText(self._generated_token)

        self.btn_copy_token.setText("✓ Copiado")
        from PySide6.QtCore import QTimer
        QTimer.singleShot(2000, lambda: self.btn_copy_token.setText("📋 Copiar Token"))

    def _on_revoke_clicked(self, token_id: str):
        """Revoke a derived token."""
        reply = QMessageBox.question(
            self,
            "Confirmar Revocación",
            "¿Estás seguro de revocar este token?\n\n"
            "Esta acción no se puede deshacer. El dispositivo que use\n"
            "este token dejará de funcionar inmediatamente.",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Start revoke worker
            self.revoke_worker = TokenRevokeWorker(self.token, token_id)
            self.revoke_worker.revoke_result.connect(self._on_token_revoked)
            self.revoke_worker.start()

    def _on_token_revoked(self, success: bool, token_id: str, error_msg: str):
        """Handle token revocation result."""
        if success:
            QMessageBox.information(
                self,
                "Token Revocado",
                "El token ha sido revocado exitosamente."
            )
            self._refresh_token_list()
        else:
            QMessageBox.critical(
                self,
                "Error al revocar token",
                f"No se pudo revocar el token:\n{error_msg}"
            )
