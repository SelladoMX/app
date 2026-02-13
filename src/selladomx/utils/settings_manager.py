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
        from ..config import ONBOARDING_VERSION

        self.settings.setValue("onboarding/completed", True)
        self.settings.setValue("onboarding/version", ONBOARDING_VERSION)
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
            Deprecated: Use get_token() instead.
            This stores the API key in QSettings (encrypted on disk by OS).
            For production, consider using keyring library for better security.
        """
        return self.get_token()

    def get_token(self) -> Optional[str]:
        """Get the stored authentication token.

        Returns:
            Token string (smx_xxxxx format) or None

        Note:
            Falls back to old api/key for backward compatibility.
        """
        token = self.settings.value("api/token", None, type=str)
        if not token:
            # Fallback to old api/key for transition
            token = self.settings.value("api/key", None, type=str)
        if token:
            logger.info("Token found in settings")
        return token

    def set_api_key(self, api_key: str):
        """Store API key.

        Args:
            api_key: The API key to store.

        Note:
            Deprecated: Use set_token() instead.
            API key is stored encrypted on disk by QSettings.
            Never log or display the full API key.
        """
        self.set_token(api_key)

    def set_token(self, token: str):
        """Store authentication token.

        Args:
            token: Token string to store (encrypted by OS)

        Note:
            Token is stored encrypted on disk by QSettings.
            Never log or display the full token.
        """
        self.settings.setValue("api/token", token)
        # Clear old key if exists
        if self.settings.contains("api/key"):
            self.settings.remove("api/key")
        self.settings.sync()
        logger.info("Token saved")

    def get_token_info(self) -> dict:
        """Get stored token metadata.

        Returns:
            dict: {
                "is_primary": bool,
                "alias": str or None,
                "expires_at": str (ISO) or None,
                "is_active": bool
            }
        """
        return {
            "is_primary": self.settings.value("api/token_is_primary", True, type=bool),
            "alias": self.settings.value("api/token_alias", None, type=str),
            "expires_at": self.settings.value("api/token_expires_at", None, type=str),
            "is_active": self.settings.value("api/token_is_active", True, type=bool),
        }

    def set_token_info(self, token_info: dict):
        """Store token metadata from API response.

        Args:
            token_info: Token info dict from /api/v1/balance response
        """
        self.settings.setValue(
            "api/token_is_primary", token_info.get("is_primary", True)
        )
        self.settings.setValue("api/token_alias", token_info.get("alias"))
        self.settings.setValue("api/token_expires_at", token_info.get("expires_at"))
        self.settings.setValue("api/token_is_active", token_info.get("is_active", True))
        self.settings.sync()

    def is_token_expired(self) -> bool:
        """Check if stored token has expired.

        Returns:
            bool: True if token is expired
        """
        expires_at_str = self.settings.value("api/token_expires_at", None, type=str)
        if not expires_at_str:
            return False  # No expiration set

        from datetime import datetime

        try:
            expires_at = datetime.fromisoformat(expires_at_str.replace("Z", "+00:00"))
            return datetime.now(expires_at.tzinfo) >= expires_at
        except (ValueError, AttributeError) as e:
            logger.warning(f"Failed to parse expiration date: {e}")
            return False

    def clear_token(self):
        """Clear stored token and all metadata."""
        self.settings.remove("api/token")
        self.settings.remove("api/token_is_primary")
        self.settings.remove("api/token_alias")
        self.settings.remove("api/token_expires_at")
        self.settings.remove("api/token_is_active")
        self.settings.remove("api/last_balance")
        self.settings.sync()
        logger.info("Token and metadata cleared")

    def clear_api_key(self):
        """Remove stored API key.

        Note:
            Deprecated: Use clear_token() instead.
        """
        self.clear_token()

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

        return self.settings.value("tsa/use_professional", True, type=bool)

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

    # ========================================================================
    # URL SCHEME REGISTRATION
    # ========================================================================

    def has_attempted_url_scheme_registration(self) -> bool:
        """Check if we've already attempted URL scheme registration.

        Returns:
            True if registration was attempted, False otherwise.
        """
        return self.settings.value("system/url_scheme_registered", False, type=bool)

    def mark_url_scheme_registration_attempted(self):
        """Mark that URL scheme registration has been attempted."""
        self.settings.setValue("system/url_scheme_registered", True)
        self.settings.sync()

    # ========================================================================
    # CERTIFICATE PATH PERSISTENCE
    # ========================================================================

    def get_last_cert_path(self) -> str:
        """Get last used certificate (.cer) path.

        Returns:
            Last used certificate path, or empty string if not set.
        """
        return self.settings.value("certificate/last_cert_path", "", type=str)

    def set_last_cert_path(self, path: str):
        """Save last used certificate path.

        Args:
            path: Path to certificate (.cer) file.
        """
        self.settings.setValue("certificate/last_cert_path", path)
        self.settings.sync()
        logger.debug(f"Saved certificate path: {path}")

    def get_last_key_path(self) -> str:
        """Get last used private key (.key) path.

        Returns:
            Last used private key path, or empty string if not set.
        """
        return self.settings.value("certificate/last_key_path", "", type=str)

    def set_last_key_path(self, path: str):
        """Save last used private key path.

        Args:
            path: Path to private key (.key) file.
        """
        self.settings.setValue("certificate/last_key_path", path)
        self.settings.sync()
        logger.debug(f"Saved private key path: {path}")

    def clear_certificate_paths(self):
        """Clear saved certificate paths."""
        self.settings.remove("certificate/last_cert_path")
        self.settings.remove("certificate/last_key_path")
        self.settings.sync()
        logger.info("Cleared certificate paths")
