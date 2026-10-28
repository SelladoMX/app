"""asn1crypto parsing fixes for SAT e.firma certificates."""

from asn1crypto import x509 as asn1_x509
from asn1crypto.core import Choice, OctetBitString


class UniqueIdentifier(Choice):
    """x500UniqueIdentifier (2.5.4.45) as a BIT STRING or a directory string.

    X.520 defines it as a BIT STRING, which is what asn1crypto expects. SAT
    e.firma certificates put the RFC there as a string, so asn1crypto fails on
    any use of the subject and pyhanko can't build a trust path for them.
    """

    _alternatives = [
        ("bit_string", OctetBitString),
        *asn1_x509.DirectoryString._alternatives,
    ]


def install() -> None:
    """Registers :class:`UniqueIdentifier` for 2.5.4.45 process-wide.

    Must run before any certificate subject is parsed. Certificates are
    re-encoded byte for byte, so signatures over them are unaffected.
    """
    asn1_x509.NameTypeAndValue._oid_specs["unique_identifier"] = UniqueIdentifier
