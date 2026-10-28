"""Tests para TSAClient y FailoverTimeStamper"""

import asyncio
import importlib
import time
from unittest.mock import patch

import pytest
import requests
from asn1crypto import tsp
from pyhanko.sign.timestamps.api import dummy_digest

from selladomx import config
from selladomx.errors import TSAResponseError, TSATimeoutError, TSAUnavailableError
from selladomx.signing import tsa as tsa_module
from selladomx.signing.tsa import FailoverTimeStamper, TSAClient

URLS = ["https://a.example", "https://b.example", "http://c.example"]

GRANTED = object()


def _rejection() -> tsp.TimeStampResp:
    return tsp.TimeStampResp(
        {"status": {"status": "rejection", "status_string": ["bad request"]}}
    )


@pytest.fixture
def fake_network():
    """Route provider requests to ``behaviour[url]`` (a value or an exception)."""
    behaviour = {}
    calls = []

    def post(url, body, timeout):
        calls.append(url)
        outcome = behaviour[url]
        if callable(outcome):
            return outcome()
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome

    real_handle = tsa_module.handle_tsp_response

    def handle(response, nonce):
        return "token" if response is GRANTED else real_handle(response, nonce)

    with patch.object(tsa_module, "_post_timestamp_request", side_effect=post):
        with patch.object(tsa_module, "handle_tsp_response", side_effect=handle):
            yield behaviour, calls


def _timestamp(stamper):
    return asyncio.run(stamper.async_timestamp(dummy_digest("sha256"), "sha256"))


class TestFailoverTimeStamper:
    def test_first_provider_success(self, fake_network):
        behaviour, calls = fake_network
        behaviour.update({u: GRANTED for u in URLS})

        assert _timestamp(FailoverTimeStamper(URLS)) == "token"
        assert calls == [URLS[0]]

    def test_connection_error_falls_back_and_remembers_provider(self, fake_network):
        behaviour, calls = fake_network
        behaviour[URLS[0]] = requests.ConnectionError("blocked")
        behaviour[URLS[1]] = GRANTED
        stamper = FailoverTimeStamper(URLS)

        assert _timestamp(stamper) == "token"
        assert stamper.preferred_url == URLS[1]
        assert _timestamp(stamper) == "token"
        assert calls == [URLS[0], URLS[1], URLS[1]]

    def test_rejected_status_falls_back(self, fake_network):
        behaviour, calls = fake_network
        behaviour[URLS[0]] = _rejection()
        behaviour[URLS[1]] = tsa_module._BadTSAResponse("unexpected Content-Type")
        behaviour[URLS[2]] = GRANTED

        assert _timestamp(FailoverTimeStamper(URLS)) == "token"
        assert calls == URLS

    def test_malformed_body_falls_back(self, fake_network):
        behaviour, _ = fake_network
        behaviour[URLS[0]] = tsp.TimeStampResp.load(b"\x30\x03\x02\x01\x00")
        behaviour[URLS[1]] = GRANTED

        assert _timestamp(FailoverTimeStamper(URLS)) == "token"

    def test_preferred_provider_failing_wraps_around(self, fake_network):
        behaviour, calls = fake_network
        behaviour[URLS[0]] = GRANTED
        behaviour[URLS[1]] = GRANTED
        behaviour[URLS[2]] = requests.ConnectionError("down")
        stamper = FailoverTimeStamper(URLS)
        stamper._preferred_index = 2

        assert _timestamp(stamper) == "token"
        assert calls == [URLS[2], URLS[0]]

    def test_all_unreachable(self, fake_network):
        behaviour, calls = fake_network
        behaviour.update({u: requests.ConnectionError("blocked") for u in URLS})

        with pytest.raises(TSAUnavailableError) as exc_info:
            _timestamp(FailoverTimeStamper(URLS))
        assert "antivirus" in str(exc_info.value)
        assert calls == URLS

    def test_all_timeouts(self, fake_network):
        behaviour, _ = fake_network
        behaviour.update({u: requests.ReadTimeout("slow") for u in URLS})

        with pytest.raises(TSATimeoutError):
            _timestamp(FailoverTimeStamper(URLS))

    def test_all_rejected(self, fake_network):
        behaviour, _ = fake_network
        behaviour.update({u: _rejection() for u in URLS})

        with pytest.raises(TSAResponseError):
            _timestamp(FailoverTimeStamper(URLS))

    def test_mixed_blocked_and_bad_responses_reports_unreachable(self, fake_network):
        behaviour, _ = fake_network
        behaviour[URLS[0]] = requests.ConnectionError("blocked")
        behaviour[URLS[1]] = requests.ConnectionError("blocked")
        behaviour[URLS[2]] = tsa_module._BadTSAResponse("HTTP 403")

        with pytest.raises(TSAUnavailableError) as exc_info:
            _timestamp(FailoverTimeStamper(URLS))
        assert not isinstance(exc_info.value, TSATimeoutError)

    def test_hung_provider_is_abandoned_after_attempt_timeout(self, fake_network):
        behaviour, _ = fake_network
        behaviour[URLS[0]] = lambda: time.sleep(2) or GRANTED
        behaviour[URLS[1]] = GRANTED
        stamper = FailoverTimeStamper(URLS, attempt_timeout=0.2, total_timeout=5)

        start = time.monotonic()
        assert _timestamp(stamper) == "token"
        assert time.monotonic() - start < 1.5
        assert stamper.preferred_url == URLS[1]

    def test_total_timeout_bounds_all_attempts(self, fake_network):
        behaviour, calls = fake_network
        behaviour.update({u: (lambda: time.sleep(2) or GRANTED) for u in URLS})
        stamper = FailoverTimeStamper(URLS, attempt_timeout=0.3, total_timeout=0.5)

        start = time.monotonic()
        with pytest.raises(TSATimeoutError):
            _timestamp(stamper)
        assert time.monotonic() - start < 1.5
        assert len(calls) == 2


class TestTSAClient:
    def test_default_providers_start_over_https_and_end_with_freetsa(self):
        client = TSAClient()
        assert client.primary_url == config.TSA_FREE_PROVIDERS[0]
        assert client.providers == config.TSA_FREE_PROVIDERS
        assert client.providers[0].startswith("https:")
        freetsa = [i for i, u in enumerate(client.providers) if "freetsa" in u]
        assert freetsa == list(
            range(len(client.providers) - len(freetsa), len(client.providers))
        )

    def test_custom_url_goes_first(self):
        client = TSAClient(tsa_url="https://example.com/tsa")
        assert client.providers[0] == "https://example.com/tsa"
        assert len(client.providers) == len(config.TSA_FREE_PROVIDERS) + 1

    def test_fallback_disabled(self):
        client = TSAClient(tsa_url="https://example.com/tsa", enable_fallback=False)
        assert client.providers == ["https://example.com/tsa"]

    def test_timestamper_is_shared_for_the_batch(self):
        client = TSAClient()
        assert client.get_timestamper() is client.get_timestamper()

    def test_env_override_goes_first_without_duplicates(self, monkeypatch):
        override = "http://timestamp.digicert.com"
        monkeypatch.setenv("SELLADOMX_FREE_TSA_URL", override)
        try:
            reloaded = importlib.reload(config)
            assert reloaded.TSA_FREE_PROVIDERS[0] == override
            assert reloaded.TSA_FREE_PROVIDERS.count(override) == 1
        finally:
            monkeypatch.delenv("SELLADOMX_FREE_TSA_URL")
            importlib.reload(config)


@pytest.mark.network
@pytest.mark.parametrize("url", config.TSA_FREE_PROVIDERS)
def test_provider_returns_valid_token(url):
    """Each configured provider answers a real request on its own."""
    stamper = FailoverTimeStamper([url])
    token = _timestamp(stamper)
    assert token["content_type"].native == "signed_data"


@pytest.mark.network
def test_failover_skips_unreachable_provider_for_real():
    stamper = FailoverTimeStamper(
        ["https://127.0.0.1:9/tsr", config.TSA_FREE_PROVIDERS[0]],
        attempt_timeout=15,
    )
    token = _timestamp(stamper)
    assert token["content_type"].native == "signed_data"
    assert stamper.preferred_url == config.TSA_FREE_PROVIDERS[0]
