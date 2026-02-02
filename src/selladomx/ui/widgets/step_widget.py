"""Step widget for guided workflow."""
from enum import Enum
from PySide6.QtCore import Signal, Property, Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSpacerItem,
    QSizePolicy,
    QGraphicsDropShadowEffect,
)
from PySide6.QtGui import QColor


class StepState(Enum):
    """State of a step in the workflow."""

    PENDING = "pending"      # Not started
    ACTIVE = "active"        # In progress
    COMPLETED = "completed"  # Finished
    DISABLED = "disabled"    # Not available


class StepWidget(QWidget):
    """Widget representing a single step in a guided workflow.

    Features:
    - Visual states (pending, active, completed, disabled)
    - Step number and title display
    - Customizable content area
    - State change signals
    """

    step_completed = Signal()
    state_changed = Signal(StepState)

    def __init__(
        self,
        step_number: int,
        title: str,
        description: str = "",
        parent=None
    ):
        """Initialize step widget.

        Args:
            step_number: Step number (1, 2, 3, etc.)
            title: Step title
            description: Step description (optional)
            parent: Parent widget
        """
        super().__init__(parent)
        self.step_number = step_number
        self.title = title
        self.description = description
        self._state = StepState.PENDING
        self._content_widget = None

        self.setObjectName("StepWidget")
        self._setup_ui()
        self._update_state_style()

    def _setup_ui(self):
        """Setup the user interface."""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        # Header with number, title, and status indicator
        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)

        # Step number - modern circular badge
        self.number_label = QLabel(str(self.step_number))
        self.number_label.setObjectName("step-number")
        self.number_label.setProperty("class", "step-number")
        self.number_label.setFixedSize(56, 56)
        self.number_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(self.number_label)

        # Title and description
        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)

        self.title_label = QLabel(self.title)
        self.title_label.setProperty("class", "step-title")
        text_layout.addWidget(self.title_label)

        if self.description:
            self.desc_label = QLabel(self.description)
            self.desc_label.setProperty("class", "step-description")
            self.desc_label.setWordWrap(True)
            text_layout.addWidget(self.desc_label)

        header_layout.addLayout(text_layout)
        header_layout.addStretch()

        # Status indicator (colored circle)
        self.status_indicator = QLabel()
        self.status_indicator.setProperty("class", "status-indicator")
        self.status_indicator.setFixedSize(14, 14)
        header_layout.addWidget(self.status_indicator)

        self.main_layout.addLayout(header_layout)

        # Content container (to be filled by set_content)
        self.content_container = QWidget()
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 10, 0, 0)
        self.content_layout.setSpacing(10)
        self.main_layout.addWidget(self.content_container)

    @Property(str)
    def state_property(self) -> str:
        """Get state as string for QSS property.

        Returns:
            State value as string
        """
        return self._state.value

    @property
    def state(self) -> StepState:
        """Get current state.

        Returns:
            Current step state
        """
        return self._state

    @state.setter
    def state(self, new_state: StepState):
        """Set step state.

        Args:
            new_state: New step state
        """
        if self._state != new_state:
            old_state = self._state
            self._state = new_state
            self._update_state_style()
            self.state_changed.emit(new_state)

            if new_state == StepState.COMPLETED and old_state != StepState.COMPLETED:
                self.step_completed.emit()

    def _update_state_style(self):
        """Update widget styling based on current state."""
        # Update property for QSS
        self.setProperty("state", self._state.value)
        self.number_label.setProperty("state", self._state.value)
        self.status_indicator.setProperty("state", self._state.value)

        # No shadows - keep it clean and simple

        # Enable/disable content based on state
        self.content_container.setEnabled(
            self._state in (StepState.ACTIVE, StepState.COMPLETED)
        )

        # Force style refresh on all widgets that have state property
        for widget in [self, self.number_label, self.status_indicator]:
            widget.style().unpolish(widget)
            widget.style().polish(widget)
            widget.update()

    def set_content(self, widget: QWidget):
        """Set the content widget for this step.

        Args:
            widget: Widget to display in the content area
        """
        # Remove old content
        if self._content_widget:
            self.content_layout.removeWidget(self._content_widget)
            self._content_widget.deleteLater()

        # Add new content
        self._content_widget = widget
        self.content_layout.addWidget(widget)

    def mark_completed(self):
        """Mark this step as completed."""
        self.state = StepState.COMPLETED

    def activate(self):
        """Activate this step."""
        self.state = StepState.ACTIVE

    def disable(self):
        """Disable this step."""
        self.state = StepState.DISABLED

    def reset(self):
        """Reset step to pending state."""
        self.state = StepState.PENDING
