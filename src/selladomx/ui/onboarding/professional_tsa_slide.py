"""Professional TSA slide for onboarding - conversion optimization."""
from PySide6.QtCore import Qt
from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpacerItem,
    QSizePolicy,
    QFrame,
)

from ...config import BUY_CREDITS_URL, CREDIT_PRICE_DISPLAY
from ..design_tokens import Colors, Typography, Spacing, BorderRadius


class ProfessionalTSASlide(QWidget):
    """Fourth slide: Introduce TSA Professional value proposition."""

    def __init__(self, parent=None):
        """Initialize professional TSA slide."""
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, Spacing.XXL, 50, Spacing.XXL)
        layout.setSpacing(Spacing.LG)

        # Top spacer
        layout.addSpacerItem(
            QSpacerItem(Spacing.XL, 10, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )

        # Icon - larger for impact
        icon_label = QLabel("⚖️")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet(f"font-size: 72px;")
        layout.addWidget(icon_label)

        layout.addSpacing(Spacing.XL)

        # Title - more prominent
        title = QLabel("¿Necesitas Validez Legal?")
        title.setAlignment(Qt.AlignCenter)
        title.setWordWrap(True)
        title.setStyleSheet(
            f"color: {Colors.TEXT_PRIMARY}; "
            f"font-size: {Typography.FONT_4XL}px; "
            f"font-weight: {Typography.WEIGHT_BOLD}; "
            f"line-height: {Typography.LINE_HEIGHT_TIGHT};"
        )
        layout.addWidget(title)

        layout.addSpacing(Spacing.XL)

        # Comparison Container
        comparison_layout = QHBoxLayout()
        comparison_layout.setSpacing(Spacing.LG)

        # TSA Professional Box
        pro_box = self._create_comparison_box(
            title="TSA Profesional",
            title_color=Colors.PRIMARY,
            features=[
                "✓ Certificación oficial RFC 3161",
                "✓ Evidencia admisible en juicios",
                "✓ Cumplimiento NOM-151-SCFI-2016",
                f"✓ Solo {CREDIT_PRICE_DISPLAY} por documento",
            ],
            is_premium=True,
        )
        comparison_layout.addWidget(pro_box, 1)

        # TSA Gratuito Box
        basic_box = self._create_comparison_box(
            title="TSA Gratuito (Limitado)",
            title_color=Colors.TEXT_TERTIARY,
            features=[
                "• Solo para uso personal e informal",
                "• ⚠️ Sin garantía de validez legal",
                "• ❌ No aceptado en procesos legales",
                "• No recomendado para negocios",
            ],
            is_premium=False,
        )
        comparison_layout.addWidget(basic_box, 1)

        layout.addLayout(comparison_layout)

        layout.addSpacing(Spacing.XL)

        # Call to Action
        cta_label = QLabel("💡 Recomendación: Usa TSA Profesional para documentos importantes como contratos, facturas o trámites oficiales")
        cta_label.setAlignment(Qt.AlignCenter)
        cta_label.setWordWrap(True)
        cta_label.setStyleSheet(
            f"color: {Colors.PRIMARY}; "
            f"font-size: {Typography.FONT_MD}px; "
            f"font-weight: {Typography.WEIGHT_MEDIUM};"
        )
        layout.addWidget(cta_label)

        # Bottom spacer
        layout.addSpacerItem(
            QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )

    def _create_comparison_box(
        self, title: str, title_color: str, features: list[str], is_premium: bool
    ) -> QFrame:
        """Create a comparison box for TSA tier."""
        box = QFrame()

        # Different styling for premium vs basic - more professional
        if is_premium:
            box.setStyleSheet(
                f"""
                QFrame {{
                    background: qlineargradient(
                        x1:0, y1:0, x2:0, y2:1,
                        stop:0 {Colors.PRIMARY_SUBTLE},
                        stop:1 {Colors.BG_ELEVATED}
                    );
                    border: 3px solid {Colors.PRIMARY};
                    border-radius: {BorderRadius.XXXL}px;
                    padding: {Spacing.XXL}px;
                }}
                """
            )
        else:
            box.setStyleSheet(
                f"""
                QFrame {{
                    background-color: {Colors.SURFACE_DEFAULT};
                    border: 2px solid {Colors.BORDER_DEFAULT};
                    border-radius: {BorderRadius.XXXL}px;
                    padding: {Spacing.XXL}px;
                }}
                """
            )

        layout = QVBoxLayout(box)
        layout.setSpacing(Spacing.MD)
        layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)

        # Title - more prominent
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(
            f"color: {title_color}; "
            f"font-size: {Typography.FONT_2XL}px; "
            f"font-weight: {Typography.WEIGHT_BOLD};"
        )
        layout.addWidget(title_label)

        layout.addSpacing(Spacing.MD)

        # Features - better readability
        for feature_text in features:
            feature_label = QLabel(feature_text)
            feature_label.setWordWrap(True)
            feature_label.setStyleSheet(
                f"color: {Colors.TEXT_PRIMARY}; "
                f"font-size: {Typography.FONT_LG}px; "
                f"padding: {Spacing.XS}px 0; "
                f"line-height: {Typography.LINE_HEIGHT_RELAXED};"
            )
            layout.addWidget(feature_label)

        return box

    def open_pricing_page(self):
        """Open the buy credits URL in default browser."""
        QDesktopServices.openUrl(QUrl(BUY_CREDITS_URL))
