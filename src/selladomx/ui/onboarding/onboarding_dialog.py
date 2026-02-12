"""Main onboarding dialog."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QStackedWidget,
    QWidget,
    QSpacerItem,
    QSizePolicy,
)

from .welcome_slide import WelcomeSlide
from .security_slide import SecuritySlide
from .professional_tsa_slide import ProfessionalTSASlide
from .howto_slide import HowToSlide
from ..design_tokens import Colors, Typography, Spacing, BorderRadius


class OnboardingDialog(QDialog):
    """Onboarding dialog with multiple slides."""

    def __init__(self, parent=None):
        """Initialize onboarding dialog.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Bienvenido a SelladoMX")
        self.setModal(True)
        self.setFixedSize(700, 500)

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Slides stack (4 slides now: Welcome, Security, Professional TSA, How To)
        self.slides_stack = QStackedWidget()
        self.slides_stack.addWidget(WelcomeSlide())
        self.slides_stack.addWidget(SecuritySlide())
        self.slides_stack.addWidget(ProfessionalTSASlide())  # New conversion slide
        self.slides_stack.addWidget(HowToSlide())
        layout.addWidget(self.slides_stack)

        # Navigation buttons - Apple style
        nav_widget = QWidget()
        nav_widget.setStyleSheet(
            f"""
            QWidget {{
                background-color: {Colors.BG_SECONDARY};
                border-top: 1px solid {Colors.BORDER_DEFAULT};
            }}
            """
        )
        nav_layout = QHBoxLayout(nav_widget)
        nav_layout.setContentsMargins(Spacing.XL, Spacing.LG, Spacing.XL, Spacing.LG)
        nav_layout.setSpacing(Spacing.MD)

        # Skip button
        self.skip_button = QPushButton("Omitir")
        self.skip_button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: transparent;
                color: {Colors.TEXT_TERTIARY};
                border: none;
                padding: {Spacing.SM}px {Spacing.LG}px;
                font-size: {Typography.FONT_BASE}px;
            }}
            QPushButton:hover {{
                color: {Colors.PRIMARY};
            }}
            """
        )
        nav_layout.addWidget(self.skip_button)

        nav_layout.addStretch()

        # Previous button
        self.prev_button = QPushButton("Anterior")
        self.prev_button.setEnabled(False)
        self.prev_button.setMinimumWidth(100)
        self.prev_button.setMinimumHeight(36)
        self.prev_button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {Colors.SURFACE_DEFAULT};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: {BorderRadius.LG}px;
                padding: 0 {Spacing.LG}px;
                font-size: {Typography.FONT_BASE}px;
            }}
            QPushButton:hover {{
                background-color: {Colors.BG_HOVER};
            }}
            QPushButton:disabled {{
                background-color: {Colors.BG_SECONDARY};
                color: {Colors.TEXT_DISABLED};
                border-color: {Colors.BORDER_SUBTLE};
            }}
            """
        )
        nav_layout.addWidget(self.prev_button)

        # Next/Start button
        self.next_button = QPushButton("Siguiente")
        self.next_button.setMinimumWidth(100)
        self.next_button.setMinimumHeight(36)
        self.next_button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {Colors.PRIMARY};
                color: {Colors.TEXT_PRIMARY};
                border: none;
                border-radius: {BorderRadius.LG}px;
                padding: 0 {Spacing.LG}px;
                font-size: {Typography.FONT_BASE}px;
                font-weight: {Typography.WEIGHT_MEDIUM};
            }}
            QPushButton:hover {{
                background-color: {Colors.PRIMARY_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {Colors.PRIMARY_ACTIVE};
            }}
            """
        )
        nav_layout.addWidget(self.next_button)

        layout.addWidget(nav_widget)

    def _connect_signals(self):
        """Connect button signals."""
        self.skip_button.clicked.connect(self._on_skip)
        self.prev_button.clicked.connect(self._on_previous)
        self.next_button.clicked.connect(self._on_next)

    def _on_skip(self):
        """Handle skip button click."""
        self.accept()

    def _on_previous(self):
        """Handle previous button click."""
        current_index = self.slides_stack.currentIndex()
        if current_index > 0:
            self.slides_stack.setCurrentIndex(current_index - 1)
            self._update_navigation_buttons()

    def _on_next(self):
        """Handle next button click."""
        current_index = self.slides_stack.currentIndex()
        total_slides = self.slides_stack.count()

        if current_index < total_slides - 1:
            # Go to next slide
            self.slides_stack.setCurrentIndex(current_index + 1)
            self._update_navigation_buttons()
        else:
            # Last slide - start the app
            self.accept()

    def _update_navigation_buttons(self):
        """Update navigation buttons based on current slide."""
        current_index = self.slides_stack.currentIndex()
        total_slides = self.slides_stack.count()

        # Previous button
        self.prev_button.setEnabled(current_index > 0)

        # Next button text
        if current_index == total_slides - 1:
            self.next_button.setText("Comenzar")
            self.next_button.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: {Colors.SUCCESS};
                    color: {Colors.TEXT_PRIMARY};
                    border: none;
                    border-radius: {BorderRadius.LG}px;
                    padding: 0 {Spacing.LG}px;
                    font-size: {Typography.FONT_BASE}px;
                    font-weight: {Typography.WEIGHT_SEMIBOLD};
                    min-width: 110px;
                }}
                QPushButton:hover {{
                    background-color: {Colors.PRIMARY_HOVER};
                }}
                QPushButton:pressed {{
                    background-color: {Colors.PRIMARY_ACTIVE};
                }}
                """
            )
        else:
            self.next_button.setText("Siguiente")
            self.next_button.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: {Colors.PRIMARY};
                    color: {Colors.TEXT_PRIMARY};
                    border: none;
                    border-radius: {BorderRadius.LG}px;
                    padding: 0 {Spacing.LG}px;
                    font-size: {Typography.FONT_BASE}px;
                    font-weight: {Typography.WEIGHT_MEDIUM};
                }}
                QPushButton:hover {{
                    background-color: {Colors.PRIMARY_HOVER};
                }}
                QPushButton:pressed {{
                    background-color: {Colors.PRIMARY_ACTIVE};
                }}
                """
            )

        # Skip button (hide on last slide)
        self.skip_button.setVisible(current_index < total_slides - 1)
