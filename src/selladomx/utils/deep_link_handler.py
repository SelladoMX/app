"""Deep link handler for SelladoMX magic links."""
from PySide6.QtCore import QObject, Signal
from urllib.parse import urlparse, parse_qs
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class DeepLinkHandler(QObject):
    """Handle selladomx:// deep links for token auto-configuration."""

    token_received = Signal(str)  # Emits token when valid URL is processed

    def __init__(self):
        super().__init__()

    def handle_url(self, url: str):
        """Parse and validate deep link URL.

        Args:
            url: Deep link URL (selladomx://auth?token=XXX)
        """
        token = self._extract_token(url)
        if token:
            logger.info("Valid token received via deep link")
            self.token_received.emit(token)
        else:
            logger.warning("Invalid deep link URL received")

    def _extract_token(self, url: str) -> Optional[str]:
        """Extract token from deep link URL.

        Args:
            url: Deep link URL

        Returns:
            Token string if valid, None otherwise
        """
        try:
            # Parse URL
            parsed = urlparse(url)

            # Validate scheme
            if parsed.scheme != "selladomx":
                logger.error(f"Invalid scheme: {parsed.scheme}")
                return None

            # Validate path (should be 'auth')
            if parsed.netloc != "auth" and parsed.path.strip("/") != "auth":
                logger.error(f"Invalid path: {parsed.netloc or parsed.path}")
                return None

            # Extract token from query params
            params = parse_qs(parsed.query)
            token = params.get("token", [None])[0]

            if not token:
                logger.error("Missing token parameter")
                return None

            # Validate token format
            from selladomx.api.client import SelladoMXAPIClient

            if not SelladoMXAPIClient.validate_token_format(token):
                logger.error("Invalid token format")
                return None

            return token

        except Exception as e:
            logger.error(f"Error parsing deep link: {e}")
            return None
