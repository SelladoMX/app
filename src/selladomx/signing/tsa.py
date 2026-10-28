"""Cliente TSA para sellado de tiempo"""

import asyncio
import base64
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Sequence

import requests
from asn1crypto import cms, tsp
from pyhanko.sign.timestamps import TimeStamper
from pyhanko.sign.timestamps.common_utils import (
    TimestampRequestError,
    handle_tsp_response,
)

from ..config import (
    TSA_CONNECT_TIMEOUT,
    TSA_FREE_PROVIDERS,
    TSA_TIMEOUT,
    TSA_TOTAL_TIMEOUT,
)
from ..errors import (
    TSAError,
    TSAResponseError,
    TSATimeoutError,
    TSAUnavailableError,
)

logger = logging.getLogger(__name__)

FAILURE_UNREACHABLE = "unreachable"
FAILURE_TIMEOUT = "timeout"
FAILURE_REJECTED = "rejected"

_TSA_REPLY_CONTENT_TYPES = (
    "application/timestamp-reply",
    "application/timestamp-response",
)

# A dedicated pool instead of asyncio's default executor: asyncio.run() joins
# the default executor on exit, so a request that outlived its wait_for()
# would keep blocking the signing call.
_REQUEST_EXECUTOR = ThreadPoolExecutor(max_workers=4, thread_name_prefix="tsa")


class _BadTSAResponse(Exception):
    pass


def _post_timestamp_request(url: str, body: bytes, timeout: float) -> tsp.TimeStampResp:
    response = requests.post(
        url,
        data=body,
        headers={
            "Content-Type": "application/timestamp-query",
            "Accept": "application/timestamp-reply",
        },
        # A short connect timeout moves past hosts whose packets are dropped
        timeout=(min(TSA_CONNECT_TIMEOUT, timeout), timeout),
    )
    if response.status_code != 200:
        raise _BadTSAResponse(f"HTTP {response.status_code}")
    content_type = response.headers.get("Content-Type", "").split(";")[0].strip()
    if content_type.lower() not in _TSA_REPLY_CONTENT_TYPES:
        raise _BadTSAResponse(f"unexpected Content-Type {content_type!r}")
    return tsp.TimeStampResp.load(response.content)


def _error_for_failures(kinds: Sequence[str]) -> TSAError:
    if kinds and all(kind == FAILURE_REJECTED for kind in kinds):
        return TSAResponseError()
    if kinds and all(kind == FAILURE_TIMEOUT for kind in kinds):
        return TSATimeoutError()
    return TSAUnavailableError()


class FailoverTimeStamper(TimeStamper):
    """Timestamper that tries several RFC 3161 providers in order.

    The provider that last succeeded is tried first on the next request, so a
    batch doesn't wait on a blocked provider for every document.
    """

    def __init__(
        self,
        urls: Sequence[str],
        attempt_timeout: float = TSA_TIMEOUT,
        total_timeout: float = TSA_TOTAL_TIMEOUT,
    ):
        """
        Args:
            urls: Provider URLs in order of preference
            attempt_timeout: Seconds allowed per provider attempt
            total_timeout: Seconds allowed for all attempts of one timestamp
        """
        if not urls:
            raise ValueError("At least one TSA URL is required")
        super().__init__()
        self.urls = list(urls)
        self.attempt_timeout = attempt_timeout
        self.total_timeout = total_timeout
        self._preferred_index = 0

    @property
    def preferred_url(self) -> str:
        return self.urls[self._preferred_index]

    async def async_timestamp(self, message_digest, md_algorithm) -> cms.ContentInfo:
        loop = asyncio.get_running_loop()
        deadline = loop.time() + self.total_timeout
        start = self._preferred_index
        order = list(range(start, len(self.urls))) + list(range(start))
        failures: list[str] = []

        for index in order:
            url = self.urls[index]
            remaining = deadline - loop.time()
            if remaining <= 0:
                logger.warning(
                    f"TSA time budget of {self.total_timeout}s exhausted, "
                    f"skipping {url} and any remaining providers"
                )
                break
            timeout = min(self.attempt_timeout, remaining)
            nonce, req = self.request_cms(message_digest, md_algorithm)
            try:
                response = await asyncio.wait_for(
                    loop.run_in_executor(
                        _REQUEST_EXECUTOR,
                        _post_timestamp_request,
                        url,
                        req.dump(),
                        timeout,
                    ),
                    timeout,
                )
                token = handle_tsp_response(response, nonce)
            except (asyncio.TimeoutError, requests.Timeout) as e:
                kind, reason = FAILURE_TIMEOUT, f"no response within {timeout:.0f}s"
                logger.debug(f"Timeout detail for {url}: {e!r}")
            except requests.RequestException as e:
                kind, reason = FAILURE_UNREACHABLE, f"{type(e).__name__}: {e}"
            except (_BadTSAResponse, TimestampRequestError) as e:
                kind, reason = FAILURE_REJECTED, str(e)
            except Exception as e:
                kind, reason = FAILURE_REJECTED, f"malformed response ({e!r})"
            else:
                if index != self._preferred_index:
                    logger.info(f"Switching preferred TSA to {url}")
                self._preferred_index = index
                logger.info(f"Timestamp obtained from {url}")
                return token

            failures.append(kind)
            logger.warning(f"TSA {url} failed ({kind}): {reason}")

        error = _error_for_failures(failures)
        logger.error(
            f"All TSA providers failed ({len(failures)} attempted): "
            f"{type(error).__name__}"
        )
        raise error


class TSAClient:
    """Free timestamping with HTTPS-first failover across public providers."""

    def __init__(
        self,
        tsa_url: Optional[str] = None,
        timeout: float = TSA_TIMEOUT,
        enable_fallback: bool = True,
    ):
        """
        Inicializa el cliente TSA.

        Args:
            tsa_url: Provider to try first (None = first of TSA_FREE_PROVIDERS)
            timeout: Seconds allowed per provider attempt
            enable_fallback: If False, only ``tsa_url`` (or the first provider) is used
        """
        self.primary_url = tsa_url or TSA_FREE_PROVIDERS[0]
        if enable_fallback:
            self.providers = [self.primary_url] + [
                url for url in TSA_FREE_PROVIDERS if url != self.primary_url
            ]
        else:
            self.providers = [self.primary_url]
        self._timestamper = FailoverTimeStamper(self.providers, attempt_timeout=timeout)
        logger.info(f"TSA client initialized with providers: {self.providers}")

    def get_timestamper(self) -> FailoverTimeStamper:
        """
        Returns the shared timestamper, so the provider that worked last is
        reused for the rest of the batch.

        Returns:
            FailoverTimeStamper over the configured providers
        """
        return self._timestamper


class APITimeStamper(TimeStamper):
    """Timestamper that proxies through the SelladoMX API to Certum TSA.

    pyhanko calls async_request_tsa_response during signing with the signature
    digest. This class forwards the TimeStampReq to the API, which contacts
    Certum and returns the full TimeStampResp for embedding in the PDF.
    """

    def __init__(
        self, api_client, filename, size_bytes, signer_cn="", signer_serial=""
    ):
        super().__init__()
        self.api_client = api_client
        self.filename = filename
        self.size_bytes = size_bytes
        self.signer_cn = signer_cn
        self.signer_serial = signer_serial
        # Stored after the real TSA call completes
        self.record_id: Optional[str] = None
        self.verification_url: Optional[str] = None
        self.credits_remaining: Optional[int] = None

    async def async_request_tsa_response(
        self, req: tsp.TimeStampReq
    ) -> tsp.TimeStampResp:
        """Send TimeStampReq to SelladoMX API, which forwards to Certum."""
        tsa_req_b64 = base64.b64encode(req.dump()).decode("ascii")

        response = self.api_client.request_tsa_sign(
            tsa_req_b64=tsa_req_b64,
            filename=self.filename,
            size_bytes=self.size_bytes,
            signer_cn=self.signer_cn,
            signer_serial=self.signer_serial,
        )

        self.record_id = response["record_id"]
        self.verification_url = response.get("verification_url", "")
        self.credits_remaining = response.get("credits_remaining")

        tsa_resp_bytes = base64.b64decode(response["tsa_resp_b64"])
        return tsp.TimeStampResp.load(tsa_resp_bytes)

    async def async_timestamp(self, message_digest, md_algorithm) -> cms.ContentInfo:
        try:
            return await super().async_timestamp(message_digest, md_algorithm)
        except (TimestampRequestError, KeyError, TypeError, ValueError) as e:
            logger.error(f"Professional TSA returned an invalid response: {e!r}")
            raise TSAResponseError(
                "El servicio de sellado profesional envió una respuesta no válida. "
                "Inténtalo de nuevo más tarde."
            ) from e

    async def async_dummy_response(self, md_algorithm):
        # pyhanko's default implementation requests a real timestamp, which
        # here would spend a credit. PDFSigner always passes bytes_reserved, so
        # pyhanko never needs a dummy.
        raise RuntimeError(
            "APITimeStamper cannot produce dummy responses; pass bytes_reserved"
        )
