"""Settings manager for SelladoMX using QSettings."""
import logging
from typing import Optional

from PySide6.QtCore import QSettings

logger = logging.getLogger(__name__)


class SettingsManager:
    """Manage application settings and preferences."""

    def __init__(self):
        """Initialize settings manager."""
        self.settings = QSettings("SelladoMX", "SelladoMX")

    # ========================================================================
    # ONBOARDING
    # ========================================================================

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

    # ========================================================================
    # API KEY (for Professional TSA tier)
    # ========================================================================

    def has_api_key(self) -> bool:
        """Check if user has configured an API key.

        Returns:
            True if API key is configured, False otherwise.
        """
        api_key = self.get_api_key()
        return api_key is not None and len(api_key) > 0

    def get_api_key(self) -> Optional[str]:
        """Get the stored API key.

        Returns:
            API key if configured, None otherwise.

        Note:
            This stores the API key in QSettings (encrypted on disk by OS).
            For production, consider using keyring library for better security.
        """
        api_key = self.settings.value("api/key", None, type=str)
        if api_key:
            logger.info("API key found in settings")
        return api_key

    def set_api_key(self, api_key: str):
        """Store API key.

        Args:
            api_key: The API key to store.

        Note:
            API key is stored encrypted on disk by QSettings.
            Never log or display the full API key.
        """
        self.settings.setValue("api/key", api_key)
        self.settings.sync()
        logger.info(f"API key stored (prefix: {api_key[:8]}...)")

    def clear_api_key(self):
        """Remove stored API key."""
        self.settings.remove("api/key")
        self.settings.sync()
        logger.info("API key cleared")

    # ========================================================================
    # TSA PREFERENCES
    # ========================================================================

    def use_professional_tsa(self) -> bool:
        """Check if user prefers professional TSA (requires credits).

        Returns:
            True if professional TSA is preferred, False for free TSA.
        """
        # Default to False (free TSA) if not set or no API key
        if not self.has_api_key():
            return False

        return self.settings.value("tsa/use_professional", False, type=bool)

    def set_use_professional_tsa(self, enabled: bool):
        """Set preference for professional TSA.

        Args:
            enabled: True to use professional TSA, False for free TSA.
        """
        self.settings.setValue("tsa/use_professional", enabled)
        self.settings.sync()
        logger.info(f"Professional TSA preference: {enabled}")

    def get_last_credit_balance(self) -> int:
        """Get last known credit balance (cached).

        Returns:
            Last known balance, or 0 if not cached.
        """
        return self.settings.value("api/last_balance", 0, type=int)

    def set_last_credit_balance(self, balance: int):
        """Cache credit balance.

        Args:
            balance: Credit balance to cache.
        """
        self.settings.setValue("api/last_balance", balance)
        self.settings.sync()
