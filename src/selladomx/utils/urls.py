"""Checks for URLs that come from the API before the app opens them."""

from typing import Optional
from urllib.parse import quote, urlparse

from ..config import API_BASE_URL

_LOCAL_HOSTS = frozenset({"localhost", "127.0.0.1"})


def is_trusted_api_url(url: str, api_base_url: Optional[str] = None) -> bool:
    """Check that a server-supplied URL points at the SelladoMX API host.

    Accepts https URLs on the same host and port as the API. Plain http is
    accepted only when the API itself is a local http development server.

    Args:
        url: URL to check
        api_base_url: API base URL to compare against (defaults to API_BASE_URL)

    Returns:
        True if the URL is safe to open in the browser
    """
    base = urlparse(api_base_url or API_BASE_URL)
    try:
        parsed = urlparse(url.strip()) if isinstance(url, str) else None
        if parsed is None or not parsed.hostname:
            return False
        if parsed.username or parsed.password:
            return False
        if parsed.hostname.lower() != (base.hostname or "").lower():
            return False
        if parsed.port != base.port:
            return False
    except ValueError:
        return False

    if parsed.scheme == "https":
        return True
    return (
        parsed.scheme == "http"
        and base.scheme == "http"
        and parsed.hostname in _LOCAL_HOSTS
    )


def verification_page_url(
    verification_token: str, api_base_url: Optional[str] = None
) -> str:
    """Build the public verification page URL for a timestamped document.

    Args:
        verification_token: Token returned by the API for the document
        api_base_url: API base URL (defaults to API_BASE_URL)

    Returns:
        URL of the verification page, or an empty string if the token is empty
    """
    if not verification_token:
        return ""
    base = (api_base_url or API_BASE_URL).rstrip("/")
    return f"{base}/verify/{quote(str(verification_token), safe='')}"
