"""Configuración centralizada"""
from pathlib import Path
from typing import Final

# TSA - Free Tier (Multi-provider with fallback)
TSA_FREE_PROVIDERS: Final[list[str]] = [
    "http://timestamp.digicert.com",  # Primary: DigiCert (most reliable)
    "http://timestamp.sectigo.com",   # Backup: Sectigo
    "https://freetsa.org/tsr",        # Fallback: FreeTSA
]
TSA_URL: Final[str] = TSA_FREE_PROVIDERS[0]  # Default to DigiCert
TSA_TIMEOUT: Final[int] = 30

# TSA - Paid Tier (Professional)
API_BASE_URL: Final[str] = "https://api.selladomx.com"
PAID_TSA_PROVIDER: Final[str] = "certum"  # Certum eIDAS

# Validación
OCSP_TIMEOUT: Final[int] = 10
CRL_TIMEOUT: Final[int] = 15
ENABLE_CRL_FALLBACK: Final[bool] = True

# Archivos
SIGNED_SUFFIX: Final[str] = "_firmado"

# Seguridad
LOG_SENSITIVE_DATA: Final[bool] = False

# UI
ONBOARDING_VERSION: Final[int] = 1
WINDOW_WIDTH: Final[int] = 900
WINDOW_HEIGHT: Final[int] = 700
