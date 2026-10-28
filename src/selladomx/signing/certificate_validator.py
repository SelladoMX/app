"""Validación de certificados e.firma"""

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Tuple

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec
from cryptography.hazmat.primitives.serialization import pkcs12
from asn1crypto import keys as asn1_keys

from ..config import LOG_SENSITIVE_DATA
from ..errors import (
    CertificateError,
    CertificateExpiredError,
    CertificateKeyMismatchError,
    CertificatePasswordError,
    CertificateValidationError,
)

logger = logging.getLogger(__name__)

PrivateKey = rsa.RSAPrivateKey | ec.EllipticCurvePrivateKey


def _is_password_error(error: ValueError) -> bool:
    message = str(error).lower()
    return "password" in message or "decrypt" in message


def _is_encrypted_pkcs8(key_data: bytes) -> bool:
    """SAT .key files are DER EncryptedPrivateKeyInfo."""
    try:
        info = asn1_keys.EncryptedPrivateKeyInfo.load(key_data, strict=True)
        info["encryption_algorithm"]["algorithm"].native
        return True
    except Exception:
        return False


def _common_name(cert: x509.Certificate) -> str:
    attrs = cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)
    return attrs[0].value if attrs else "?"


class CertificateValidator:
    """Validador de certificados e.firma del SAT"""

    def __init__(self, cert_path: Path, key_path: Path, password: str):
        """
        Inicializa el validador.

        Args:
            cert_path: Ruta al archivo .cer (certificado)
            key_path: Ruta al archivo .key (clave privada)
            password: Contraseña de la clave privada
        """
        self.cert_path = Path(cert_path)
        self.key_path = Path(key_path)
        self.password = password.encode() if password else None

        if LOG_SENSITIVE_DATA:
            logger.debug(f"Certificate path: {cert_path}")
            logger.debug(f"Key path: {key_path}")
        else:
            logger.info("Certificate validator initialized")

    def validate_all(self) -> Tuple[x509.Certificate, PrivateKey]:
        """
        Valida el certificado completamente y carga la clave privada.

        Returns:
            Tupla (certificado, clave_privada)

        Raises:
            CertificateError: Si hay un error cargando los archivos
            CertificateExpiredError: Si el certificado está expirado
            CertificateValidationError: Si falla la validación
        """
        cert = self._load_certificate()
        logger.info(f"Certificate loaded: CN={_common_name(cert)}")

        private_key = self._load_private_key()
        logger.info("Private key loaded successfully")

        self._validate_key_matches(cert, private_key)

        self._validate_validity(cert)

        self._validate_revocation(cert)

        logger.info("Certificate validation successful")
        return cert, private_key

    def _load_certificate(self) -> x509.Certificate:
        """Carga el certificado desde el archivo .cer (DER o PEM)"""
        if not self.cert_path.exists():
            raise CertificateError(
                f"Archivo de certificado no encontrado: {self.cert_path}"
            )

        try:
            with open(self.cert_path, "rb") as f:
                cert_data = f.read()

            # Intentar DER primero (formato común en e.firma)
            try:
                return x509.load_der_x509_certificate(cert_data, default_backend())
            except Exception:
                return x509.load_pem_x509_certificate(cert_data, default_backend())

        except Exception as e:
            logger.error(f"Error loading certificate: {e}")
            raise CertificateError(f"No se pudo cargar el certificado: {e}")

    def _load_private_key(self) -> PrivateKey:
        """Carga la clave privada desde el archivo .key (DER, PEM o PKCS#12)"""
        if not self.key_path.exists():
            raise CertificateError(
                f"Archivo de clave privada no encontrado: {self.key_path}"
            )

        try:
            with open(self.key_path, "rb") as f:
                key_data = f.read()
        except OSError as e:
            logger.error(f"Error reading private key file: {e.strerror}")
            raise CertificateError(f"No se pudo leer la clave privada: {e.strerror}")

        password_rejected = False
        missing_password = False
        for loader in (self._load_der_key, self._load_pem_key, self._load_pkcs12_key):
            try:
                private_key = loader(key_data, self.password)
            except TypeError as e:
                if "not given" in str(e).lower():
                    missing_password = True
                    logger.debug(f"{loader.__name__}: key is encrypted")
                    continue
                # Unencrypted key but the user typed a password anyway
                try:
                    private_key = loader(key_data, None)
                except Exception as retry_error:
                    logger.debug(f"{loader.__name__} failed: {retry_error}")
                    continue
            except ValueError as e:
                if _is_password_error(e):
                    password_rejected = True
                logger.debug(f"{loader.__name__} failed: {e}")
                continue
            except Exception as e:
                logger.debug(f"{loader.__name__} failed: {e}")
                continue
            if private_key is not None:
                return private_key

        if missing_password:
            raise CertificatePasswordError(
                "La clave privada está protegida. Escribe su contraseña."
            )
        if password_rejected or _is_encrypted_pkcs8(key_data):
            raise CertificatePasswordError(
                "Contraseña incorrecta. Verifica la contraseña de tu clave "
                "privada (.key)."
            )
        raise CertificateError(
            "No se pudo cargar la clave privada. Verifica que el archivo .key "
            "sea correcto y esté en un formato compatible (DER, PEM o PKCS#12)."
        )

    @staticmethod
    def _load_der_key(key_data: bytes, password: Optional[bytes]):
        return serialization.load_der_private_key(
            key_data, password=password, backend=default_backend()
        )

    @staticmethod
    def _load_pem_key(key_data: bytes, password: Optional[bytes]):
        return serialization.load_pem_private_key(
            key_data, password=password, backend=default_backend()
        )

    @staticmethod
    def _load_pkcs12_key(key_data: bytes, password: Optional[bytes]):
        private_key, _, _ = pkcs12.load_key_and_certificates(
            key_data, password, backend=default_backend()
        )
        return private_key

    @staticmethod
    def _validate_key_matches(cert: x509.Certificate, private_key: PrivateKey):
        """Verifica que la clave privada corresponda al certificado"""

        def spki(public_key) -> bytes:
            return public_key.public_bytes(
                serialization.Encoding.DER,
                serialization.PublicFormat.SubjectPublicKeyInfo,
            )

        if spki(cert.public_key()) != spki(private_key.public_key()):
            logger.error("Private key does not match the certificate")
            raise CertificateKeyMismatchError(
                "La clave privada (.key) no corresponde al certificado (.cer). "
                "Verifica que ambos archivos sean de la misma e.firma."
            )

    def _validate_validity(self, cert: x509.Certificate) -> None:
        """Valida que el certificado esté dentro de su período de vigencia"""
        now = datetime.now(timezone.utc)

        # not_valid_*_utc existe desde cryptography 42; versiones anteriores solo
        # tienen not_valid_*, que devuelve datetimes naive
        try:
            not_before = cert.not_valid_before_utc
            not_after = cert.not_valid_after_utc
        except AttributeError:
            not_before = cert.not_valid_before
            not_after = cert.not_valid_after
            if not_before.tzinfo is None:
                not_before = not_before.replace(tzinfo=timezone.utc)
            if not_after.tzinfo is None:
                not_after = not_after.replace(tzinfo=timezone.utc)

        if now < not_before:
            raise CertificateValidationError(
                f"El certificado aún no es válido. Válido desde: {not_before}"
            )

        if now > not_after:
            raise CertificateExpiredError(f"El certificado expiró el: {not_after}")

        logger.info(f"Certificate validity OK (expires: {not_after})")

    def _validate_revocation(self, cert: x509.Certificate) -> None:
        """
        Punto de validación de revocación del certificado.

        No consulta OCSP ni CRL, así que un certificado revocado no se detecta.
        """
        logger.info("Certificate revocation status is not checked")

    def get_certificate_info(self, cert: x509.Certificate) -> dict:
        """
        Extrae información útil del certificado.

        Args:
            cert: Certificado a analizar

        Returns:
            Diccionario con información del certificado
        """
        try:
            not_before = cert.not_valid_before_utc
            not_after = cert.not_valid_after_utc
        except AttributeError:
            not_before = cert.not_valid_before
            not_after = cert.not_valid_after
            if not_before.tzinfo is None:
                not_before = not_before.replace(tzinfo=timezone.utc)
            if not_after.tzinfo is None:
                not_after = not_after.replace(tzinfo=timezone.utc)

        info = {
            "subject": cert.subject.rfc4514_string(),
            "issuer": cert.issuer.rfc4514_string(),
            "serial_number": format(cert.serial_number, "x"),
            "not_before": not_before.isoformat(),
            "not_after": not_after.isoformat(),
        }

        try:
            cn_attrs = cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)
            if cn_attrs:
                info["common_name"] = cn_attrs[0].value
        except Exception:
            pass

        return info
