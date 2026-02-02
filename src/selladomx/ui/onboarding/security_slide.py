"""Security slide for onboarding."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpacerItem, QSizePolicy


class SecuritySlide(QWidget):
    """Second slide: Security and privacy features."""

    def __init__(self, parent=None):
        """Initialize security slide."""
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

        # Icon
        icon_label = QLabel("🔒")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 56px;")
        layout.addWidget(icon_label)

        layout.addSpacing(20)

        # Title
        title = QLabel("Tu privacidad es nuestra prioridad")
        title.setAlignment(Qt.AlignCenter)
        title.setWordWrap(True)
        title.setStyleSheet(
            "font-size: 24px; font-weight: 600; color: #1D1D1F;"
        )
        layout.addWidget(title)

        layout.addSpacing(24)

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
            feature_layout.setContentsMargins(20, 6, 20, 6)

            # Bullet
            bullet_label = QLabel(bullet)
            bullet_label.setStyleSheet("font-size: 18px; color: #007AFF;")
            bullet_label.setFixedWidth(20)
            feature_layout.addWidget(bullet_label)

            # Text
            text_label = QLabel(text)
            text_label.setWordWrap(True)
            text_label.setStyleSheet(
                "font-size: 14px; color: #1D1D1F;"
            )
            feature_layout.addWidget(text_label, 1)

            layout.addLayout(feature_layout)

        # Bottom spacer
        layout.addSpacerItem(
            QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )
