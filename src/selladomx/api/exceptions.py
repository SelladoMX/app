"""Custom exceptions for SelladoMX API client."""


class APIError(Exception):
    """Base exception for API-related errors."""

    def __init__(self, message: str, status_code: int = None):
        """Initialize API error.

        Args:
            message: Error message
            status_code: HTTP status code (if applicable)
        """
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class AuthenticationError(APIError):
    """Raised when API authentication fails (invalid or missing API key)."""

    pass


class InsufficientCreditsError(APIError):
    """Raised when user doesn't have enough credits for the operation."""

    def __init__(self, message: str = "Sin créditos disponibles", available_credits: int = 0):
        """Initialize insufficient credits error.

        Args:
            message: Error message
            available_credits: Number of credits currently available
        """
        self.available_credits = available_credits
        super().__init__(message)


class NetworkError(APIError):
    """Raised when network/connection issues occur."""

    pass
