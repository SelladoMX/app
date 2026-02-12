"""SettingsBridge - Exposes SettingsManager to QML."""
import logging

from PySide6.QtCore import QObject, Signal, Slot, Property

from ...utils.settings_manager import SettingsManager

logger = logging.getLogger(__name__)


class SettingsBridge(QObject):
    """Bridge to expose SettingsManager to QML.

    This provides QML-friendly access to application settings
    with signals for property changes.
    """

    # Signals
    lastCertPathChanged = Signal()
    lastKeyPathChanged = Signal()
    hasApiKeyChanged = Signal()
    onboardingCompletedChanged = Signal()

    def __init__(self, settings_manager: SettingsManager):
        """Initialize the settings bridge.

        Args:
            settings_manager: Settings manager instance
        """
        super().__init__()
        self.settings = settings_manager

        logger.info("SettingsBridge initialized")

    # ========================================================================
    # CERTIFICATE PATHS
    # ========================================================================

    @Property(str, notify=lastCertPathChanged)
    def lastCertPath(self) -> str:
        """Get last used certificate path (property for QML)."""
        return self.settings.get_last_cert_path()

    @Property(str, notify=lastKeyPathChanged)
    def lastKeyPath(self) -> str:
        """Get last used private key path (property for QML)."""
        return self.settings.get_last_key_path()

    # ========================================================================
    # API KEY / TOKEN
    # ========================================================================

    @Property(bool, notify=hasApiKeyChanged)
    def hasApiKey(self) -> bool:
        """Check if API key is configured (property for QML)."""
        return self.settings.has_api_key()

    @Slot(result=str)
    def getToken(self) -> str:
        """Get the stored token (callable from QML).

        Returns:
            Token string or empty string if not set
        """
        token = self.settings.get_token()
        return token or ""

    @Slot(str)
    def setToken(self, token: str):
        """Set the authentication token (callable from QML).

        Args:
            token: Token string to store
        """
        self.settings.set_token(token)
        self.hasApiKeyChanged.emit()
        logger.info("Token saved via SettingsBridge")

    @Slot()
    def clearToken(self):
        """Clear the stored token (callable from QML)."""
        self.settings.clear_token()
        self.hasApiKeyChanged.emit()
        logger.info("Token cleared via SettingsBridge")

    # ========================================================================
    # ONBOARDING
    # ========================================================================

    @Property(bool, notify=onboardingCompletedChanged)
    def hasCompletedOnboarding(self) -> bool:
        """Check if onboarding was completed (property for QML)."""
        return self.settings.has_completed_onboarding()

    @Slot()
    def markOnboardingCompleted(self):
        """Mark onboarding as completed (callable from QML)."""
        self.settings.mark_onboarding_completed()
        self.onboardingCompletedChanged.emit()
        logger.info("Onboarding marked as completed")

    @Slot()
    def resetOnboarding(self):
        """Reset onboarding status (callable from QML)."""
        self.settings.reset_onboarding()
        self.onboardingCompletedChanged.emit()
        logger.info("Onboarding reset")

    # ========================================================================
    # TSA PREFERENCES
    # ========================================================================

    @Slot(result=bool)
    def useProfessionalTSA(self) -> bool:
        """Check if professional TSA is preferred (callable from QML).

        Returns:
            True if professional TSA is preferred
        """
        return self.settings.use_professional_tsa()

    @Slot(bool)
    def setUseProfessionalTSA(self, enabled: bool):
        """Set professional TSA preference (callable from QML).

        Args:
            enabled: True to use professional TSA
        """
        self.settings.set_use_professional_tsa(enabled)
        logger.info(f"Professional TSA preference set to: {enabled}")

    @Slot(result=int)
    def getLastCreditBalance(self) -> int:
        """Get last known credit balance (callable from QML).

        Returns:
            Last known balance
        """
        return self.settings.get_last_credit_balance()

    @Slot(int)
    def setLastCreditBalance(self, balance: int):
        """Set cached credit balance (callable from QML).

        Args:
            balance: Credit balance to cache
        """
        self.settings.set_last_credit_balance(balance)
