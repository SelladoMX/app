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

from ..design_tokens import Colors, Typography, Spacing, BorderRadius


class HowToSlide(QWidget):
    """Third slide: How to use the application."""

    def __init__(self, parent=None):
        """Initialize how-to slide."""
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, Spacing.XXL, 50, Spacing.XXL)
        layout.setSpacing(Spacing.MD)

        # Top spacer
        layout.addSpacerItem(
            QSpacerItem(Spacing.XL, Spacing.XL, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )

        # Title
        title = QLabel("Cómo funciona")
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
        subtitle = QLabel("3 pasos simples")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; "
            f"font-size: {Typography.FONT_LG}px;"
        )
        layout.addWidget(subtitle)

        layout.addSpacing(Spacing.XXL)

        # Steps - clean and simple
        steps = [
            ("1.", "Seleccionaaa los PDFs que deseas firmar"),
            ("2.", "Carga tu certificado e.firma (.cer y .key)"),
            ("3.", "Haz clic en 'Firmar' y listo"),
        ]

        for number, text in steps:
            step_layout = QHBoxLayout()
            step_layout.setSpacing(10)
            step_layout.setContentsMargins(Spacing.XL, Spacing.SM, Spacing.XL, Spacing.SM)

            # Number
            number_label = QLabel(number)
            number_label.setStyleSheet(
                f"color: {Colors.PRIMARY}; "
                f"font-size: {Typography.FONT_XL}px; "
                f"font-weight: {Typography.WEIGHT_SEMIBOLD};"
            )
            number_label.setFixedWidth(Spacing.XXL)
            step_layout.addWidget(number_label)

            # Text
            text_label = QLabel(text)
            text_label.setWordWrap(True)
            text_label.setStyleSheet(
                f"color: {Colors.TEXT_PRIMARY}; "
                f"font-size: {Typography.FONT_MD}px;"
            )
            step_layout.addWidget(text_label, 1)

            layout.addLayout(step_layout)

        layout.addSpacing(Spacing.XL)

        # Final message
        message = QLabel("Tus documentos nunca salen de tu computadora.")
        message.setAlignment(Qt.AlignCenter)
        message.setWordWrap(True)
        message.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; "
            f"font-size: {Typography.FONT_MD}px; "
            f"font-style: italic;"
        )
        layout.addWidget(message)

        # Bottom spacer
        layout.addSpacerItem(
            QSpacerItem(Spacing.XL, Spacing.XL, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )
