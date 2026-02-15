"""Configuración centralizada"""

import logging
import os
import sys
from typing import Final

logger = logging.getLogger(__name__)

# ============================================================================
# ENVIRONMENT-BASED CONFIGURATION
# ============================================================================

# API Configuration - can be overridden via environment variable
# Set SELLADOMX_API_URL to point to a different API endpoint (e.g., local dev)
API_BASE_URL: str = os.environ.get(
    "SELLADOMX_API_URL",
    "https://www.selladomx.com",  # Production default
)

# Log which API is being used (for debugging)
logger.info(f"Using API base URL: {API_BASE_URL}")

# ============================================================================
# TSA CONFIGURATION
# ============================================================================

# TSA - Free Tier (Multi-provider with fallback)
# Override with SELLADOMX_FREE_TSA_URL environment variable
_DEFAULT_FREE_TSA = "http://timestamp.digicert.com"
TSA_FREE_PROVIDERS: Final[list[str]] = [
    os.environ.get("SELLADOMX_FREE_TSA_URL", _DEFAULT_FREE_TSA),
    "http://timestamp.sectigo.com",  # Backup: Sectigo
    "https://freetsa.org/tsr",  # Fallback: FreeTSA
]
TSA_URL: Final[str] = TSA_FREE_PROVIDERS[0]  # Default to first provider
TSA_TIMEOUT: Final[int] = 30

# TSA - Paid Tier (Professional)
# Override with SELLADOMX_PROFESSIONAL_TSA_PROVIDER environment variable
PAID_TSA_PROVIDER: Final[str] = os.environ.get(
    "SELLADOMX_PROFESSIONAL_TSA_PROVIDER",
    "certum",  # Certum eIDAS (default)
)
BUY_CREDITS_URL: Final[str] = f"{API_BASE_URL}/precios"

# ============================================================================
# PRICING CONFIGURATION
# ============================================================================

# Pricing
# TODO: Consider fetching from API endpoint in the future to avoid hardcoding
# For now, update these values when prices change (requires rebuild)
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
# Windows needs more padding and sharper corners
BUTTON_HEIGHT: Final[int] = 32 if IS_WINDOWS else 28
DIALOG_PADDING: Final[int] = 24 if IS_WINDOWS else 20
BORDER_RADIUS: Final[int] = 4 if IS_WINDOWS else 6  # Windows: sharper corners

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
