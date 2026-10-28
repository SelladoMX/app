"""Tests for the x500UniqueIdentifier parsing fix."""

from datetime import UTC, datetime, timedelta

import pytest
from asn1crypto import x509 as asn1_x509
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

import selladomx.signing  # noqa: F401  (installs the fix)


def _cert_with_unique_identifier(value, string_type=None):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    attribute = (
        x509.NameAttribute(NameOID.X500_UNIQUE_IDENTIFIER, value, string_type)
        if string_type
        else x509.NameAttribute(NameOID.X500_UNIQUE_IDENTIFIER, value)
    )
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "PRUEBA"), attribute])
    now = datetime.now(UTC)
    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(days=1))
        .not_valid_after(now + timedelta(days=1))
        .sign(key, hashes.SHA256())
    )
    return cert.public_bytes(serialization.Encoding.DER)


@pytest.mark.parametrize(
    "string_type", [x509.name._ASN1Type.PrintableString, x509.name._ASN1Type.UTF8String]
)
def test_rfc_as_string_parses(string_type):
    der = _cert_with_unique_identifier("XAXX010101000", string_type)
    cert = asn1_x509.Certificate.load(der)

    assert cert.subject.native["unique_identifier"] == "XAXX010101000"
    assert "XAXX010101000" in cert.subject.human_friendly
    assert cert.dump(force=True) == der


def test_standard_bit_string_still_parses():
    der = _cert_with_unique_identifier(b"\x00\x01\x02", x509.name._ASN1Type.BitString)
    cert = asn1_x509.Certificate.load(der)

    assert isinstance(cert.subject.native["unique_identifier"], bytes)
    assert cert.dump(force=True) == der
