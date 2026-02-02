"""How-to slide for onboarding."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)


class HowToSlide(QWidget):
    """Third slide: How to use the application."""

    def __init__(self, parent=None):
        """Initialize how-to slide."""
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 30, 50, 30)
        layout.setSpacing(12)

        # Top spacer
        layout.addSpacerItem(
            QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )

        # Title
        title = QLabel("Cómo funciona")
        title.setAlignment(Qt.AlignCenter)
        title.setWordWrap(True)
        title.setStyleSheet("font-size: 24px; font-weight: 600; color: #1D1D1F;")
        layout.addWidget(title)

        layout.addSpacing(8)

        # Subtitle
        subtitle = QLabel("3 pasos simples")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 15px; color: #86868B;")
        layout.addWidget(subtitle)

        layout.addSpacing(24)

        # Steps - clean and simple
        steps = [
            ("1.", "Seleccionaaa los PDFs que deseas firmar"),
            ("2.", "Carga tu certificado e.firma (.cer y .key)"),
            ("3.", "Haz clic en 'Firmar' y listo"),
        ]

        for number, text in steps:
            step_layout = QHBoxLayout()
            step_layout.setSpacing(10)
            step_layout.setContentsMargins(20, 8, 20, 8)

            # Number
            number_label = QLabel(number)
            number_label.setStyleSheet(
                "font-size: 16px; font-weight: 600; color: #007AFF;"
            )
            number_label.setFixedWidth(30)
            step_layout.addWidget(number_label)

            # Text
            text_label = QLabel(text)
            text_label.setWordWrap(True)
            text_label.setStyleSheet("font-size: 14px; color: #1D1D1F;")
            step_layout.addWidget(text_label, 1)

            layout.addLayout(step_layout)

        layout.addSpacing(20)

        # Final message
        message = QLabel("Tus documentos nunca salen de tu computadora.")
        message.setAlignment(Qt.AlignCenter)
        message.setWordWrap(True)
        message.setStyleSheet("font-size: 14px; color: #86868B; font-style: italic;")
        layout.addWidget(message)

        # Bottom spacer
        layout.addSpacerItem(
            QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )
