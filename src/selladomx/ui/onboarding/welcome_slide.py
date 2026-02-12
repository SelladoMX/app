"""Welcome slide for onboarding."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSpacerItem, QSizePolicy

from ..design_tokens import Colors, Typography, Spacing, BorderRadius


class WelcomeSlide(QWidget):
    """First slide: Welcome and main value proposition."""

    def __init__(self, parent=None):
        """Initialize welcome slide."""
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, Spacing.XXL, 50, Spacing.XXL)
        layout.setSpacing(Spacing.MD)

        # Top spacer
        layout.addSpacerItem(
            QSpacerItem(Spacing.XL, Spacing.XXL, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )

        # Icon - simple and clear
        icon_label = QLabel("🔐")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet(f"font-size: 56px;")
        layout.addWidget(icon_label)

        layout.addSpacing(Spacing.XL)

        # Title
        title = QLabel("Bienvenido a SelladoMX")
        title.setAlignment(Qt.AlignCenter)
        title.setWordWrap(True)
        title.setStyleSheet(
            f"color: {Colors.TEXT_PRIMARY}; "
            f"font-size: {Typography.FONT_3XL}px; "
            f"font-weight: {Typography.WEIGHT_SEMIBOLD};"
        )
        layout.addWidget(title)

        layout.addSpacing(Spacing.SM)

        # Subtitle
        subtitle = QLabel("Firma digital 100% local")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; "
            f"font-size: {Typography.FONT_LG}px;"
        )
        layout.addWidget(subtitle)

        layout.addSpacing(Spacing.XXL)

        # Main message
        message = QLabel(
            "Firma tus documentos PDF con certificados digitales "
            "sin enviar datos a servidores externos.\n\n"
            "Todo el procesamiento ocurre localmente en tu computadora."
        )
        message.setAlignment(Qt.AlignCenter)
        message.setWordWrap(True)
        message.setStyleSheet(
            f"color: {Colors.TEXT_PRIMARY}; "
            f"font-size: {Typography.FONT_MD}px; "
            f"line-height: {Typography.LINE_HEIGHT_NORMAL};"
        )
        layout.addWidget(message)

        # Bottom spacer
        layout.addSpacerItem(
            QSpacerItem(Spacing.XL, Spacing.XXL, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )
