"""Settings manager for SelladoMX using QSettings."""
from PySide6.QtCore import QSettings


class SettingsManager:
    """Manage application settings and preferences."""

    def __init__(self):
        """Initialize settings manager."""
        self.settings = QSettings("SelladoMX", "SelladoMX")

    def has_completed_onboarding(self) -> bool:
        """Check if user has completed onboarding.

        Returns:
            True if onboarding was completed, False otherwise.
        """
        return self.settings.value("onboarding/completed", False, type=bool)

    def mark_onboarding_completed(self):
        """Mark onboarding as completed."""
        self.settings.setValue("onboarding/completed", True)
        self.settings.sync()

    def reset_onboarding(self):
        """Reset onboarding status (for testing)."""
        self.settings.setValue("onboarding/completed", False)
        self.settings.sync()

    def get_onboarding_version(self) -> int:
        """Get the version of onboarding that was completed.

        Returns:
            Version number, or 0 if not completed.
        """
        return self.settings.value("onboarding/version", 0, type=int)

    def set_onboarding_version(self, version: int):
        """Set the onboarding version.

        Args:
            version: Version number to set.
        """
        self.settings.setValue("onboarding/version", version)
        self.settings.sync()
