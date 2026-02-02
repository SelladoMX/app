"""Welcome slide for onboarding."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSpacerItem, QSizePolicy


class WelcomeSlide(QWidget):
    """First slide: Welcome and main value proposition."""

    def __init__(self, parent=None):
        """Initialize welcome slide."""
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 30, 50, 30)
        layout.setSpacing(12)

        # Top spacer
        layout.addSpacerItem(
            QSpacerItem(20, 30, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )

        # Icon - simple and clear
        icon_label = QLabel("🔐")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 56px;")
        layout.addWidget(icon_label)

        layout.addSpacing(20)

        # Title
        title = QLabel("Bienvenido a SelladoMX")
        title.setAlignment(Qt.AlignCenter)
        title.setWordWrap(True)
        title.setStyleSheet(
            "font-size: 24px; font-weight: 600; color: #1D1D1F;"
        )
        layout.addWidget(title)

        layout.addSpacing(8)

        # Subtitle
        subtitle = QLabel("Firma digital 100% local")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet(
            "font-size: 15px; color: #86868B;"
        )
        layout.addWidget(subtitle)

        layout.addSpacing(24)

        # Main message
        message = QLabel(
            "Firma tus documentos PDF con certificados digitales "
            "sin enviar datos a servidores externos.\n\n"
            "Todo el procesamiento ocurre localmente en tu computadora."
        )
        message.setAlignment(Qt.AlignCenter)
        message.setWordWrap(True)
        message.setStyleSheet(
            "font-size: 14px; color: #1D1D1F; line-height: 1.5;"
        )
        layout.addWidget(message)

        # Bottom spacer
        layout.addSpacerItem(
            QSpacerItem(20, 30, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )
