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
from .howto_slide import HowToSlide


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

        # Slides stack
        self.slides_stack = QStackedWidget()
        self.slides_stack.addWidget(WelcomeSlide())
        self.slides_stack.addWidget(SecuritySlide())
        self.slides_stack.addWidget(HowToSlide())
        layout.addWidget(self.slides_stack)

        # Navigation buttons - Apple style
        nav_widget = QWidget()
        nav_widget.setStyleSheet(
            """
            QWidget {
                background-color: #FAFAFA;
                border-top: 1px solid #D2D2D7;
            }
            """
        )
        nav_layout = QHBoxLayout(nav_widget)
        nav_layout.setContentsMargins(20, 16, 20, 16)
        nav_layout.setSpacing(12)

        # Skip button
        self.skip_button = QPushButton("Omitir")
        self.skip_button.setStyleSheet(
            """
            QPushButton {
                background-color: transparent;
                color: #86868B;
                border: none;
                padding: 8px 16px;
                font-size: 13px;
            }
            QPushButton:hover {
                color: #007AFF;
            }
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
            """
            QPushButton {
                background-color: white;
                color: #1D1D1F;
                border: 1px solid #D2D2D7;
                border-radius: 8px;
                padding: 0 16px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #F5F5F7;
            }
            QPushButton:disabled {
                background-color: #FAFAFA;
                color: #C7C7CC;
                border-color: #E5E5E7;
            }
            """
        )
        nav_layout.addWidget(self.prev_button)

        # Next/Start button
        self.next_button = QPushButton("Siguiente")
        self.next_button.setMinimumWidth(100)
        self.next_button.setMinimumHeight(36)
        self.next_button.setStyleSheet(
            """
            QPushButton {
                background-color: #007AFF;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 0 16px;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #0051D5;
            }
            QPushButton:pressed {
                background-color: #004BB8;
            }
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
                """
                QPushButton {
                    background-color: #34C759;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 0 16px;
                    font-size: 13px;
                    font-weight: 600;
                    min-width: 110px;
                }
                QPushButton:hover {
                    background-color: #30B350;
                }
                QPushButton:pressed {
                    background-color: #2A9F47;
                }
                """
            )
        else:
            self.next_button.setText("Siguiente")
            self.next_button.setStyleSheet(
                """
                QPushButton {
                    background-color: #007AFF;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 0 16px;
                    font-size: 13px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #0051D5;
                }
                QPushButton:pressed {
                    background-color: #004BB8;
                }
                """
            )

        # Skip button (hide on last slide)
        self.skip_button.setVisible(current_index < total_slides - 1)
