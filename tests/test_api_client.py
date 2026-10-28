"""Tests for SelladoMXAPIClient status mapping (requests is mocked; no network)."""

from unittest.mock import MagicMock

import pytest
import requests

from selladomx.api.client import SelladoMXAPIClient
from selladomx.api.exceptions import (
    APIError,
    AuthenticationError,
    InsufficientCreditsError,
    NetworkError,
    PrimaryTokenRequiredError,
    TokenExpiredError,
    TokenRevokedError,
)


def _response(status, body=None, text=""):
    response = MagicMock(spec=requests.Response)
    response.status_code = status
    response.content = b"x" if body is not None or text else b""
    response.text = text
    if body is None:
        response.json.side_effect = requests.exceptions.JSONDecodeError("no", "", 0)
    else:
        response.json.return_value = body
    return response


@pytest.fixture
def client():
    client = SelladoMXAPIClient(api_key="smx_test", base_url="https://api.example")
    client.session = MagicMock()
    return client


def _respond(client, response):
    client.session.request.return_value = response


def test_402_insufficient_credits_reads_credits_remaining(client):
    _respond(
        client,
        _response(
            402,
            {
                "error": "insufficient_credits",
                "message": "Insufficient credits",
                "credits_remaining": 0,
            },
        ),
    )
    with pytest.raises(InsufficientCreditsError) as exc_info:
        client.request_tsa_sign("cmVx", "a.pdf", 10)
    assert exc_info.value.credits_remaining == 0
    assert exc_info.value.status_code == 402


def test_402_from_timestamp_request_endpoint(client):
    _respond(
        client,
        _response(402, {"error": "Insufficient credits", "credits_remaining": 3}),
    )
    with pytest.raises(InsufficientCreditsError) as exc_info:
        client.request_timestamp("h", "a.pdf", 1, "cn", "1")
    assert exc_info.value.credits_remaining == 3


def test_403_insufficient_credits_still_supported(client):
    _respond(
        client,
        _response(403, {"error": "insufficient_credits", "credits_remaining": 2}),
    )
    with pytest.raises(InsufficientCreditsError) as exc_info:
        client.get_balance()
    assert exc_info.value.credits_remaining == 2


def test_403_primary_token_required(client):
    _respond(
        client,
        _response(403, {"error": "Only primary tokens can create derived tokens"}),
    )
    with pytest.raises(PrimaryTokenRequiredError):
        client.derive_token("Laptop")


def test_403_other(client):
    _respond(client, _response(403, {"error": "Token does not belong to your account"}))
    with pytest.raises(APIError) as exc_info:
        client.revoke_token("id")
    assert exc_info.value.status_code == 403
    assert not isinstance(exc_info.value, InsufficientCreditsError)


@pytest.mark.parametrize(
    "error, expected",
    [
        ("Token has expired", TokenExpiredError),
        ("Token is inactive", TokenRevokedError),
    ],
)
def test_401_token_states(client, error, expected):
    _respond(client, _response(401, {"error": error}))
    with pytest.raises(expected):
        client.get_balance()


@pytest.mark.parametrize(
    "body", [{"error": "Token not found"}, {"error": "Invalid token format"}, None]
)
def test_401_generic(client, body):
    _respond(client, _response(401, body))
    with pytest.raises(AuthenticationError) as exc_info:
        client.get_balance()
    assert type(exc_info.value) is AuthenticationError


def test_500_without_json_has_generic_message(client):
    _respond(client, _response(500, None, text="<html>Bad gateway</html>"))
    with pytest.raises(APIError) as exc_info:
        client.get_balance()
    assert exc_info.value.status_code == 500
    assert "<html>" not in exc_info.value.message


def test_connection_error_is_network_error(client):
    client.session.request.side_effect = requests.ConnectionError("refused")
    with pytest.raises(NetworkError):
        client.get_balance()


def test_verify_by_hash_uses_path_parameter(client):
    _respond(client, _response(200, {"valid": True}))
    assert client.verify_by_hash("abc123") == {"valid": True}
    url = client.session.request.call_args.kwargs["url"]
    assert url == "https://api.example/api/v1/verify/by-hash/abc123"


def test_verify_by_hash_not_found(client):
    _respond(client, _response(404, {"error": "Not found"}))
    assert client.verify_by_hash("abc123") is None
