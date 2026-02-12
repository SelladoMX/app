"""Security slide for onboarding."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpacerItem, QSizePolicy

from ..design_tokens import Colors, Typography, Spacing, BorderRadius


class SecuritySlide(QWidget):
    """Second slide: Security and privacy features."""

    def __init__(self, parent=None):
        """Initialize security slide."""
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

        # Icon
        icon_label = QLabel("🔒")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet(f"font-size: 56px;")
        layout.addWidget(icon_label)

        layout.addSpacing(Spacing.XL)

        # Title
        title = QLabel("Tu privacidad es nuestra prioridad")
        title.setAlignment(Qt.AlignCenter)
        title.setWordWrap(True)
        title.setStyleSheet(
            f"color: {Colors.TEXT_PRIMARY}; "
            f"font-size: {Typography.FONT_3XL}px; "
            f"font-weight: {Typography.WEIGHT_SEMIBOLD};"
        )
        layout.addWidget(title)

        layout.addSpacing(Spacing.XXL)

        # Security features list - simple and clean
        features = [
            ("•", "Tus claves privadas nunca salen de tu computadora"),
            ("•", "Código 100% open source y auditable"),
            ("•", "Procesamiento completamente local"),
            ("•", "Los datos se limpian de memoria al cerrar"),
        ]

        for bullet, text in features:
            feature_layout = QHBoxLayout()
            feature_layout.setSpacing(10)
            feature_layout.setContentsMargins(Spacing.XL, Spacing.XS, Spacing.XL, Spacing.XS)

            # Bullet
            bullet_label = QLabel(bullet)
            bullet_label.setStyleSheet(
                f"color: {Colors.PRIMARY}; "
                f"font-size: {Typography.FONT_XL}px;"
            )
            bullet_label.setFixedWidth(Spacing.XL)
            feature_layout.addWidget(bullet_label)

            # Text
            text_label = QLabel(text)
            text_label.setWordWrap(True)
            text_label.setStyleSheet(
                f"color: {Colors.TEXT_PRIMARY}; "
                f"font-size: {Typography.FONT_MD}px;"
            )
            feature_layout.addWidget(text_label, 1)

            layout.addLayout(feature_layout)

        # Bottom spacer
        layout.addSpacerItem(
            QSpacerItem(Spacing.XL, Spacing.XL, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )
