"""Tests para PDFSigner (sin red: el TSA es local)"""

import base64
from datetime import UTC, datetime, timedelta
from io import BytesIO
from unittest.mock import MagicMock, patch

import aiohttp

import pytest
from asn1crypto import keys as asn1_keys
from asn1crypto import tsp
from asn1crypto import x509 as asn1_x509
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID
from pyhanko.pdf_utils import generic
from pyhanko.pdf_utils.reader import PdfFileReader
from pyhanko.pdf_utils.writer import PageObject, PdfFileWriter
from pyhanko.sign.timestamps import TimeStamper
from pyhanko.sign.timestamps.dummy_client import DummyTimeStamper

from selladomx.errors import PDFError, TSAResponseError, TSAUnavailableError
from selladomx.signing import pdf_signer as pdf_signer_module
from selladomx.signing.pdf_signer import (
    SIGNATURE_BYTES_RESERVED,
    PDFSigner,
    signed_output_path,
)
from selladomx.signing import tsa as tsa_module
from selladomx.signing.tsa import APITimeStamper, TSAClient


def _self_signed(cn: str, eku=None):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, cn)])
    now = datetime.now(UTC)
    builder = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(days=1))
        .not_valid_after(now + timedelta(days=30))
    )
    if eku:
        builder = builder.add_extension(x509.ExtendedKeyUsage(eku), critical=True)
    return builder.sign(key, hashes.SHA256()), key


@pytest.fixture(scope="module")
def signer_identity():
    return _self_signed("PERSONA DE PRUEBA")


@pytest.fixture(scope="module")
def tsa_identity():
    return _self_signed("TSA DE PRUEBA", eku=[ExtendedKeyUsageOID.TIME_STAMPING])


class OfflineTSA(DummyTimeStamper):
    """Local TSA that fails the test if pyhanko asks it for a dummy response."""

    def __init__(self, tsa_identity):
        cert, key = tsa_identity
        super().__init__(
            tsa_cert=asn1_x509.Certificate.load(
                cert.public_bytes(serialization.Encoding.DER)
            ),
            tsa_key=asn1_keys.PrivateKeyInfo.load(
                key.private_bytes(
                    serialization.Encoding.DER,
                    serialization.PrivateFormat.PKCS8,
                    serialization.NoEncryption(),
                )
            ),
        )
        self.requests = 0

    async def async_request_tsa_response(self, req):
        self.requests += 1
        return await super().async_request_tsa_response(req)

    async def async_dummy_response(self, md_algorithm):
        raise AssertionError("signature size estimation must not request a timestamp")


@pytest.fixture(autouse=True)
def no_aiohttp_sessions(monkeypatch):
    """Fail if pyhanko opens an aiohttp session.

    A session is bound to the event loop that created it, and the worker runs a
    new loop per file.
    """

    def refuse(*args, **kwargs):
        raise AssertionError("signing must not create an aiohttp session")

    monkeypatch.setattr(aiohttp.ClientSession, "__init__", refuse)


def _blank_pdf(path):
    writer = PdfFileWriter()
    stream = writer.add_object(generic.StreamObject(stream_data=b""))
    writer.insert_page(PageObject(contents=stream, media_box=[0, 0, 612, 792]))
    out = BytesIO()
    writer.write(out)
    path.write_bytes(out.getvalue())
    return path


def _hybrid_xref_pdf(path):
    """Write a PDF whose classic xref trailer also points at an xref stream.

    Word and other Office exporters produce this "hybrid" layout.
    """
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>",
    ]
    out = bytearray(b"%PDF-1.5\n")
    offsets = []
    for number, body in enumerate(objects, 1):
        offsets.append(len(out))
        out += b"%d 0 obj\n%s\nendobj\n" % (number, body)

    xref_stream_offset = len(out)
    rows = b"\x00\x00\x00\x00\x00\xff\xff"
    for offset in offsets + [xref_stream_offset]:
        rows += b"\x01" + offset.to_bytes(4, "big") + b"\x00\x00"
    out += (
        b"4 0 obj\n<< /Type /XRef /Size 5 /W [1 4 2] /Index [0 5] "
        b"/Root 1 0 R /Length %d >>\nstream\n" % len(rows)
    )
    out += rows + b"\nendstream\nendobj\n"

    table_offset = len(out)
    out += b"xref\n0 4\n0000000000 65535 f \n"
    for offset in offsets:
        out += b"%010d 00000 n \n" % offset
    out += (
        b"trailer\n<< /Size 5 /Root 1 0 R /XRefStm %d >>\n"
        b"startxref\n%d\n%%%%EOF\n" % (xref_stream_offset, table_offset)
    )
    path.write_bytes(bytes(out))
    return path


@pytest.fixture
def pdf(tmp_path):
    return _blank_pdf(tmp_path / "contrato.pdf")


def _signer(signer_identity, **kwargs):
    cert, key = signer_identity
    return PDFSigner(cert, key, **kwargs)


class TestSigning:
    def test_free_signing_makes_no_estimation_request(
        self, signer_identity, tsa_identity, pdf
    ):
        tsa = OfflineTSA(tsa_identity)
        tsa_client = MagicMock()
        tsa_client.get_timestamper.return_value = tsa

        output = _signer(signer_identity, tsa_client=tsa_client).sign_pdf(pdf)

        assert output.name == "contrato_firmado.pdf"
        assert tsa.requests == 1
        assert PDFSigner.verify_signature(output) is True

    def test_free_signing_uses_our_transport_once_per_file(
        self, signer_identity, tsa_identity, tmp_path
    ):
        tsa = OfflineTSA(tsa_identity)
        posted = []

        def post(url, body, timeout):
            posted.append(url)
            return tsa.request_tsa_response(tsp.TimeStampReq.load(body))

        signer = _signer(signer_identity, tsa_client=TSAClient())
        with patch.object(tsa_module, "_post_timestamp_request", side_effect=post):
            outputs = [
                signer.sign_pdf(_blank_pdf(tmp_path / f"doc{i}.pdf")) for i in range(2)
            ]

        assert len(posted) == 2
        assert all(PDFSigner.verify_signature(output) for output in outputs)

    def test_signature_contents_use_reserved_size(
        self, signer_identity, tsa_identity, pdf
    ):
        output = _signer(
            signer_identity, timestamper=OfflineTSA(tsa_identity)
        ).sign_pdf(pdf)
        with open(output, "rb") as f:
            sig = PdfFileReader(f).embedded_signatures[0]
            assert len(sig.sig_object["/Contents"].original_bytes) * 2 == (
                SIGNATURE_BYTES_RESERVED
            )

    def test_professional_signing_spends_exactly_one_request(
        self, signer_identity, tsa_identity, pdf
    ):
        certum = OfflineTSA(tsa_identity)
        calls = []

        def request_tsa_sign(tsa_req_b64, **kwargs):
            calls.append(kwargs["filename"])
            req = tsp.TimeStampReq.load(base64.b64decode(tsa_req_b64))
            resp = certum.request_tsa_response(req)
            return {
                "tsa_resp_b64": base64.b64encode(resp.dump()).decode(),
                "record_id": "rec-1",
                "verification_url": "https://selladomx.com/v/abc",
                "credits_remaining": 9,
            }

        api_client = MagicMock()
        api_client.request_tsa_sign.side_effect = request_tsa_sign
        stamper = APITimeStamper(api_client, pdf.name, pdf.stat().st_size)

        output = _signer(signer_identity, timestamper=stamper).sign_pdf(pdf)

        assert calls == ["contrato.pdf"]
        assert stamper.record_id == "rec-1"
        assert stamper.credits_remaining == 9
        assert PDFSigner.verify_signature(output) is True

    def test_professional_invalid_response_is_typed(self, signer_identity, pdf):
        rejection_der = bytes.fromhex("30053003020102")  # PKIStatus rejection
        api_client = MagicMock()
        api_client.request_tsa_sign.return_value = {
            "tsa_resp_b64": base64.b64encode(rejection_der).decode(),
            "record_id": "rec-1",
        }
        stamper = APITimeStamper(api_client, pdf.name, 1)

        with pytest.raises(TSAResponseError):
            _signer(signer_identity, timestamper=stamper).sign_pdf(pdf)

    def test_tsa_errors_propagate_unwrapped(self, signer_identity, pdf):
        class Unreachable(TimeStamper):
            async def async_timestamp(self, message_digest, md_algorithm):
                raise TSAUnavailableError()

        tsa_client = MagicMock()
        tsa_client.get_timestamper.return_value = Unreachable()

        with pytest.raises(TSAUnavailableError):
            _signer(signer_identity, tsa_client=tsa_client).sign_pdf(pdf)
        assert not (pdf.parent / "contrato_firmado.pdf").exists()

    def test_signs_pdf_with_hybrid_xref(self, signer_identity, tsa_identity, tmp_path):
        pdf = _hybrid_xref_pdf(tmp_path / "exportado_de_word.pdf")
        assert PdfFileReader(
            BytesIO(pdf.read_bytes()), strict=False
        ).xrefs.hybrid_xrefs_present

        output = _signer(
            signer_identity, timestamper=OfflineTSA(tsa_identity)
        ).sign_pdf(pdf)

        assert PDFSigner.verify_signature(output) is True

    def test_unwritable_output_fails_before_spending_a_credit(
        self, signer_identity, pdf, tmp_path
    ):
        api_client = MagicMock()
        stamper = APITimeStamper(api_client, pdf.name, 1)
        output = tmp_path / "no-existe" / "contrato_firmado.pdf"

        with pytest.raises(PDFError, match="No se pudo guardar"):
            _signer(signer_identity, timestamper=stamper).sign_pdf(pdf, output)
        api_client.request_tsa_sign.assert_not_called()

    def test_does_not_overwrite_existing_signed_copy(
        self, signer_identity, tsa_identity, pdf
    ):
        existing = pdf.parent / "contrato_firmado.pdf"
        existing.write_bytes(b"keep me")
        signer = _signer(signer_identity, timestamper=OfflineTSA(tsa_identity))

        first = signer.sign_pdf(pdf)
        second = signer.sign_pdf(pdf)

        assert existing.read_bytes() == b"keep me"
        assert first.name == "contrato_firmado (1).pdf"
        assert second.name == "contrato_firmado (2).pdf"

    def test_corrupt_pdf_raises_pdf_error(self, signer_identity, tmp_path):
        bad = tmp_path / "roto.pdf"
        bad.write_bytes(b"not a pdf")
        with pytest.raises(PDFError):
            _signer(signer_identity).sign_pdf(bad)

    def test_missing_pdf(self, signer_identity, tmp_path):
        with pytest.raises(PDFError, match="no encontrado"):
            _signer(signer_identity).sign_pdf(tmp_path / "nope.pdf")


class TestOutputPath:
    def test_default_and_output_dir(self, tmp_path):
        src = tmp_path / "a" / "x.pdf"
        assert signed_output_path(src) == tmp_path / "a" / "x_firmado.pdf"
        assert signed_output_path(src, tmp_path) == tmp_path / "x_firmado.pdf"

    def test_gives_up_instead_of_looping_forever(self, tmp_path, monkeypatch):
        monkeypatch.setattr(pdf_signer_module, "MAX_OUTPUT_NAME_ATTEMPTS", 3)
        for name in ["x_firmado.pdf"] + [f"x_firmado ({i}).pdf" for i in (1, 2, 3)]:
            (tmp_path / name).touch()
        with pytest.raises(PDFError):
            signed_output_path(tmp_path / "x.pdf")


class TestVerifySignature:
    def test_unsigned_pdf_is_not_valid(self, pdf):
        assert PDFSigner.verify_signature(pdf) is False

    def test_tampered_pdf_is_not_valid(self, signer_identity, tsa_identity, pdf):
        output = _signer(
            signer_identity, timestamper=OfflineTSA(tsa_identity)
        ).sign_pdf(pdf)
        data = bytearray(output.read_bytes())
        index = data.index(b"/MediaBox")
        data[index + 1 : index + 2] = b"X"
        output.write_bytes(bytes(data))

        assert PDFSigner.verify_signature(output) is False

    def test_missing_file(self, tmp_path):
        with pytest.raises(PDFError):
            PDFSigner.verify_signature(tmp_path / "nope.pdf")


@pytest.mark.network
def test_sign_with_real_free_tsa(signer_identity, pdf):
    from selladomx.signing.tsa import TSAClient

    output = _signer(signer_identity, tsa_client=TSAClient()).sign_pdf(pdf)
    assert PDFSigner.verify_signature(output) is True
