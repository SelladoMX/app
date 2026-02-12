"""HTTP client for SelladoMX API."""
import logging
from typing import Optional
from datetime import datetime

import requests

from ..config import API_BASE_URL
from .exceptions import (
    APIError,
    AuthenticationError,
    InsufficientCreditsError,
    InvalidTokenFormatError,
    NetworkError,
    PrimaryTokenRequiredError,
    TokenExpiredError,
    TokenRevokedError,
)

logger = logging.getLogger(__name__)


class SelladoMXAPIClient:
    """Client for SelladoMX backend API.

    This client handles:
    - User authentication via API key
    - Credit balance queries
    - Professional TSA timestamp requests
    - Certificate verification
    """

    def __init__(self, api_key: Optional[str] = None, base_url: str = API_BASE_URL):
        """Initialize API client.

        Args:
            api_key: User's API key for authentication
            base_url: Base URL for the API
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "SelladoMX/1.0",
            "Content-Type": "application/json",
        })

        if api_key:
            self.session.headers.update({
                "Authorization": f"Bearer {api_key}"
            })

        logger.info(f"API client initialized with base URL: {base_url}")

    def _request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[dict] = None,
        require_auth: bool = True
    ) -> dict:
        """Make HTTP request to API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (e.g., "/api/v1/user/balance")
            json_data: JSON payload for request body
            require_auth: Whether this endpoint requires authentication

        Returns:
            JSON response as dict

        Raises:
            AuthenticationError: If authentication is required but API key is missing/invalid
            NetworkError: If network/connection issues occur
            APIError: For other API errors
        """
        if require_auth and not self.api_key:
            raise AuthenticationError("API key is required for this operation")

        url = f"{self.base_url}{endpoint}"

        try:
            logger.debug(f"Making {method} request to {url}")
            response = self.session.request(
                method=method,
                url=url,
                json=json_data,
                timeout=30
            )

            # Handle errors
            if response.status_code == 401:
                error_data = response.json() if response.content else {}
                error_type = error_data.get("error", "")

                if error_type == "token_expired":
                    raise TokenExpiredError("Token has expired")
                elif error_type == "token_revoked":
                    raise TokenRevokedError("Token has been revoked")
                else:
                    raise AuthenticationError(
                        "API key inválido o expirado",
                        status_code=401
                    )
            elif response.status_code == 403:
                # Check if it's insufficient credits or primary token required
                try:
                    error_data = response.json()
                    if error_data.get("error") == "insufficient_credits":
                        raise InsufficientCreditsError(
                            error_data.get("message", "Sin créditos disponibles"),
                            available_credits=error_data.get("available_credits", 0)
                        )
                    elif "primary token" in error_data.get("error", "").lower():
                        raise PrimaryTokenRequiredError("Se requiere token primario")
                except ValueError:
                    pass  # Not JSON response

                raise APIError(
                    "No tienes permisos para esta operación",
                    status_code=403
                )
            elif response.status_code >= 400:
                try:
                    error_data = response.json()
                    error_msg = error_data.get("message", "Error desconocido")
                except ValueError:
                    error_msg = response.text or "Error desconocido"

                raise APIError(error_msg, status_code=response.status_code)

            # Success - return JSON
            return response.json()

        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {e}")
            raise NetworkError(f"No se pudo conectar al servidor: {e}")
        except requests.exceptions.Timeout as e:
            logger.error(f"Request timeout: {e}")
            raise NetworkError(f"Tiempo de espera agotado: {e}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            raise NetworkError(f"Error de red: {e}")

    def get_balance(self) -> dict:
        """Get available credits balance with token info.

        Returns:
            dict: {
                "credits_remaining": 150,
                "email": "user@example.com",
                "plan": "individual",
                "token_info": {
                    "is_primary": true,
                    "alias": null,
                    "expires_at": null,
                    "is_active": true
                }
            }

        Raises:
            AuthenticationError: If API key is invalid
            NetworkError: If connection fails
        """
        response = self._request("GET", "/api/v1/balance")
        credits = response.get("credits_remaining", 0)
        logger.info(f"Current balance: {credits} credits")
        return response  # Return full dict instead of just credits

    def request_timestamp(
        self,
        document_hash: str,
        filename: str,
        size_bytes: int,
        signer_cn: str,
        signer_serial: str
    ) -> dict:
        """Request professional TSA timestamp (consumes 1 credit).

        Args:
            document_hash: SHA-256 hash of the signed document
            filename: Original PDF filename
            size_bytes: Document size in bytes
            signer_cn: Signer's Common Name from certificate
            signer_serial: Certificate serial number

        Returns:
            Dictionary with:
                - tsa_token_b64: Base64-encoded RFC 3161 token
                - timestamp_utc: ISO timestamp
                - verification_token: Token for public verification URL
                - verification_url: Public URL to verify the certificate

        Raises:
            InsufficientCreditsError: If user has no credits
            AuthenticationError: If API key is invalid
            NetworkError: If connection fails
        """
        payload = {
            "document_hash": document_hash,
            "filename": filename,
            "size_bytes": size_bytes,
            "signer_cn": signer_cn,
            "signer_serial": signer_serial,
        }

        response = self._request("POST", "/api/v1/timestamp/request", json_data=payload)

        logger.info(
            f"Timestamp request successful for {filename}. "
            f"Verification URL: {response.get('verification_url')}"
        )

        return response

    def get_history(self, limit: int = 50, offset: int = 0) -> list[dict]:
        """Get user's timestamp history.

        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip

        Returns:
            List of timestamp records

        Raises:
            AuthenticationError: If API key is invalid
            NetworkError: If connection fails
        """
        response = self._request(
            "GET",
            f"/api/v1/timestamp/history?limit={limit}&offset={offset}"
        )
        return response.get("records", [])

    def verify_by_hash(self, document_hash: str) -> Optional[dict]:
        """Verify a document by its hash (public endpoint, no auth required).

        Args:
            document_hash: SHA-256 hash of the document

        Returns:
            Verification record if found, None otherwise
        """
        try:
            response = self._request(
                "GET",
                f"/api/v1/verify/by-hash?hash={document_hash}",
                require_auth=False
            )
            return response
        except APIError as e:
            if e.status_code == 404:
                return None
            raise

    def list_tokens(self) -> dict:
        """List all tokens (primary + derived) for the current user.

        Returns:
            dict: {
                "primary": {...},
                "derived": [...]
            }

        Raises:
            AuthenticationError: If API key is invalid
            NetworkError: If connection fails
        """
        return self._request("GET", "/api/v1/tokens/list")

    def derive_token(self, alias: str, expires_in_days: Optional[int] = None) -> dict:
        """Create a derived token from the primary token.

        Args:
            alias: User-friendly name for the token (1-50 chars)
            expires_in_days: Optional expiration in days

        Returns:
            dict: {
                "token": "smx_xxxxx...",  # Full token (only shown once!)
                "alias": "Laptop Juan",
                "expires_at": "2025-01-20T10:00:00Z"
            }

        Raises:
            PrimaryTokenRequiredError: If current token is not primary
            AuthenticationError: If API key is invalid
            NetworkError: If connection fails
        """
        json_data = {"alias": alias}
        if expires_in_days is not None:
            json_data["expires_in_days"] = expires_in_days
        return self._request("POST", "/api/v1/tokens/derive", json_data=json_data)

    def revoke_token(self, token_id: str) -> dict:
        """Revoke a token by ID.

        Args:
            token_id: UUID of the token to revoke

        Returns:
            dict: {"message": "Token revoked successfully"}

        Raises:
            AuthenticationError: If API key is invalid
            NetworkError: If connection fails
            APIError: If token cannot be revoked
        """
        return self._request("DELETE", f"/api/v1/tokens/{token_id}")

    @staticmethod
    def validate_token_format(token: str) -> bool:
        """Validate token format (smx_xxxxx...).

        Args:
            token: Token string to validate

        Returns:
            bool: True if valid smx_ format
        """
        import re
        return bool(re.match(r"^smx_[0-9a-f]{5,}$", token))

    def is_configured(self) -> bool:
        """Check if API client is configured with a valid API key.

        Returns:
            True if API key is set, False otherwise
        """
        return self.api_key is not None and len(self.api_key) > 0

    def test_connection(self) -> bool:
        """Test connection to API server.

        Returns:
            True if connection is successful, False otherwise
        """
        try:
            self.get_balance()
            return True
        except Exception as e:
            logger.warning(f"API connection test failed: {e}")
            return False
