"""Configuración centralizada"""
from pathlib import Path
from typing import Final

# TSA
TSA_URL: Final[str] = "https://freetsa.org/tsr"
TSA_TIMEOUT: Final[int] = 30

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
