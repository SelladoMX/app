"""Configuración centralizada"""

import logging
import os
import sys
from typing import Final
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# ============================================================================
# ENVIRONMENT-BASED CONFIGURATION
# ============================================================================

DEFAULT_API_BASE_URL: Final[str] = "https://www.selladomx.com"
_LOCAL_HOSTS: Final[frozenset[str]] = frozenset({"localhost", "127.0.0.1"})


def resolve_api_base_url(value: str | None) -> str:
    """Validate a SELLADOMX_API_URL override.

    The API receives the user's token, so only https URLs are accepted, plus
    plain http on localhost for local development.

    Args:
        value: Raw value of SELLADOMX_API_URL, or None if unset

    Returns:
        The override without a trailing slash, or DEFAULT_API_BASE_URL if it is
        unset or not allowed
    """
    if not value:
        return DEFAULT_API_BASE_URL
    try:
        parsed = urlparse(value.strip())
        host = parsed.hostname
    except ValueError:
        parsed, host = None, None
    if parsed is not None and host:
        if parsed.scheme == "https" or (
            parsed.scheme == "http" and host in _LOCAL_HOSTS
        ):
            return value.strip().rstrip("/")
    logger.warning(
        "Ignoring SELLADOMX_API_URL: only https URLs (or http on localhost) "
        f"are allowed; using {DEFAULT_API_BASE_URL}"
    )
    return DEFAULT_API_BASE_URL


API_BASE_URL: str = resolve_api_base_url(os.environ.get("SELLADOMX_API_URL"))

logger.info(f"Using API base URL: {API_BASE_URL}")

# ============================================================================
# TSA CONFIGURATION
# ============================================================================

# Free tier, in fallback order. Providers whose TSA certificates Adobe trusts
# come before freetsa, which it doesn't, even though that puts DigiCert's plain
# http (it refuses connections on port 443) ahead of freetsa's https.
_DEFAULT_FREE_TSA_PROVIDERS = [
    "https://timestamp.sectigo.com",
    "http://timestamp.digicert.com",
    "http://timestamp.sectigo.com",
    "https://freetsa.org/tsr",
    "http://freetsa.org/tsr",
]
_FREE_TSA_OVERRIDE = os.environ.get("SELLADOMX_FREE_TSA_URL")
TSA_FREE_PROVIDERS: Final[list[str]] = (
    [_FREE_TSA_OVERRIDE] if _FREE_TSA_OVERRIDE else []
) + [url for url in _DEFAULT_FREE_TSA_PROVIDERS if url != _FREE_TSA_OVERRIDE]
TSA_URL: Final[str] = TSA_FREE_PROVIDERS[0]
# Seconds per provider attempt, and for all attempts of one timestamp combined
TSA_TIMEOUT: Final[int] = 10
TSA_TOTAL_TIMEOUT: Final[int] = 30

# Paid tier
PAID_TSA_PROVIDER: Final[str] = os.environ.get(
    "SELLADOMX_PROFESSIONAL_TSA_PROVIDER",
    "certum",  # Certum eIDAS
)
BUY_CREDITS_URL: Final[str] = f"{API_BASE_URL}/precios"

# ============================================================================
# PRICING CONFIGURATION
# ============================================================================

# Hardcoded: update when prices change; takes effect only in a new build.
CREDIT_PRICE_DISPLAY: Final[str] = "desde $7 MXN"  # Minimum price (100-credit package)

# Validación
OCSP_TIMEOUT: Final[int] = 10
CRL_TIMEOUT: Final[int] = 15
ENABLE_CRL_FALLBACK: Final[bool] = True

# Archivos
SIGNED_SUFFIX: Final[str] = "_firmado"

# Seguridad
LOG_SENSITIVE_DATA: Final[bool] = False

# Debug Mode
IS_DEBUG: Final[bool] = os.environ.get("SELLADOMX_DEBUG", "0") == "1"

# Platform Detection
IS_MACOS: Final[bool] = sys.platform == "darwin"
IS_WINDOWS: Final[bool] = sys.platform == "win32"
IS_LINUX: Final[bool] = sys.platform == "linux"

# Platform-Specific Design Tokens
BUTTON_HEIGHT: Final[int] = 32 if IS_WINDOWS else 28
DIALOG_PADDING: Final[int] = 24 if IS_WINDOWS else 20
BORDER_RADIUS: Final[int] = 4 if IS_WINDOWS else 6

# Window Icons per Platform
WINDOW_ICONS: Final[dict[str, str]] = {
    "minimize": "⊖" if IS_WINDOWS else "－",
    "maximize": "⊡" if IS_WINDOWS else "□",
    "close": "✕" if IS_WINDOWS else "×",
    "settings": "⚙" if IS_WINDOWS else "⚙️",
}

# UI
ONBOARDING_VERSION: Final[int] = 1
WINDOW_WIDTH: Final[int] = 900
WINDOW_HEIGHT: Final[int] = 700

# ============================================================================
# COLORS - Must stay in sync with design/DesignTokens.qml
# ============================================================================

COLOR_SUCCESS: Final[str] = "#2e7d32"  # Green (accent/success)
COLOR_ERROR: Final[str] = "#EF4444"  # Red
COLOR_WARNING: Final[str] = "#F59E0B"  # Amber
COLOR_INFO: Final[str] = "#3B82F6"  # Blue
COLOR_MUTED: Final[str] = "#6B7280"  # Gray-500
COLOR_MUTED_LIGHT: Final[str] = "#9CA3AF"  # Gray-400
