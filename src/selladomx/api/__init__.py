"""API client module for SelladoMX backend services."""
from .client import SelladoMXAPIClient
from .exceptions import (
    APIError,
    AuthenticationError,
    InsufficientCreditsError,
    NetworkError,
)

__all__ = [
    "SelladoMXAPIClient",
    "APIError",
    "AuthenticationError",
    "InsufficientCreditsError",
    "NetworkError",
]
