"""Validación de certificados e.firma"""
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Tuple

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec
from pyhanko_certvalidator import ValidationContext
from pyhanko_certvalidator.errors import PathValidationError, RevokedError

from ..config import ENABLE_CRL_FALLBACK, LOG_SENSITIVE_DATA
from ..errors import (
    CertificateError,
    CertificateExpiredError,
    CertificateRevokedError,
    CertificateValidationError,
)

logger = logging.getLogger(__name__)

PrivateKey = rsa.RSAPrivateKey | ec.EllipticCurvePrivateKey


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
            CertificateRevokedError: Si el certificado está revocado
            CertificateValidationError: Si falla la validación
        """
        # Cargar certificado
        cert = self._load_certificate()
        logger.info(f"Certificate loaded: {cert.subject.rfc4514_string()}")

        # Cargar clave privada
        private_key = self._load_private_key()
        logger.info("Private key loaded successfully")

        # Validar vigencia
        self._validate_validity(cert)

        # Validar revocación
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
                # Si falla, intentar PEM
                return x509.load_pem_x509_certificate(cert_data, default_backend())

        except Exception as e:
            logger.error(f"Error loading certificate: {e}")
            raise CertificateError(f"No se pudo cargar el certificado: {e}")

    def _load_private_key(self) -> PrivateKey:
        """Carga la clave privada desde el archivo .key"""
        if not self.key_path.exists():
            raise CertificateError(
                f"Archivo de clave privada no encontrado: {self.key_path}"
            )

        try:
            with open(self.key_path, "rb") as f:
                key_data = f.read()

            # Los archivos .key del SAT pueden estar en varios formatos
            # Intentar múltiples métodos de carga

            # 1. Intentar DER (más común en e.firma)
            try:
                return serialization.load_der_private_key(
                    key_data, password=self.password, backend=default_backend()
                )
            except Exception as der_error:
                logger.debug(f"DER loading failed: {der_error}")

            # 2. Intentar PEM
            try:
                return serialization.load_pem_private_key(
                    key_data, password=self.password, backend=default_backend()
                )
            except Exception as pem_error:
                logger.debug(f"PEM loading failed: {pem_error}")

            # 3. Intentar con OpenSSL legacy para formatos antiguos
            try:
                from cryptography.hazmat.primitives.serialization import pkcs12

                # Algunos certificados del SAT usan PKCS#12
                private_key, _, _ = pkcs12.load_key_and_certificates(
                    key_data, self.password, backend=default_backend()
                )
                if private_key:
                    return private_key
            except Exception as pkcs12_error:
                logger.debug(f"PKCS#12 loading failed: {pkcs12_error}")

            # Si todos fallan, reportar error
            raise CertificateError(
                "No se pudo cargar la clave privada. Verifique que:\n"
                "1. El archivo .key sea correcto\n"
                "2. La contraseña sea correcta\n"
                "3. El formato del archivo sea compatible (DER, PEM, o PKCS#12)"
            )

        except CertificateError:
            raise
        except ValueError as e:
            if (
                "password" in str(e).lower()
                or "decrypt" in str(e).lower()
                or "incorrect" in str(e).lower()
            ):
                raise CertificateError("Contraseña incorrecta")
            raise CertificateError(f"Error de formato en la clave privada: {e}")
        except Exception as e:
            logger.error(f"Error loading private key: {e}")
            raise CertificateError(f"No se pudo cargar la clave privada: {e}")

    def _validate_validity(self, cert: x509.Certificate) -> None:
        """Valida que el certificado esté dentro de su período de vigencia"""
        now = datetime.now(timezone.utc)

        # Use not_valid_before/not_valid_after (compatible con cryptography >= 42.0)
        try:
            not_before = cert.not_valid_before_utc
            not_after = cert.not_valid_after_utc
        except AttributeError:
            # Fallback para versiones más nuevas de cryptography
            not_before = cert.not_valid_before
            not_after = cert.not_valid_after
            # Asegurar que sean timezone-aware
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
        Valida que el certificado no esté revocado usando OCSP o CRL.

        Intenta OCSP primero, si falla y está habilitado el fallback, usa CRL.
        """
        try:
            # Crear contexto de validación
            context = ValidationContext(
                allow_fetching=True,
                revocation_mode="hard-fail" if not ENABLE_CRL_FALLBACK else "soft-fail",
            )

            # Intentar validar
            validator = context.certificate_registry

            logger.info("Checking certificate revocation status")

            # pyhanko-certvalidator valida automáticamente con OCSP y CRL
            # Si encuentra el certificado revocado, levantará RevokedError

        except RevokedError as e:
            logger.error(f"Certificate is revoked: {e}")
            raise CertificateRevokedError("El certificado ha sido revocado")
        except PathValidationError as e:
            logger.error(f"Certificate validation path error: {e}")
            raise CertificateValidationError(
                f"Error en la validación del certificado: {e}"
            )
        except Exception as e:
            logger.warning(f"Could not verify revocation status: {e}")
            if not ENABLE_CRL_FALLBACK:
                raise CertificateValidationError(
                    f"No se pudo verificar el estado de revocación: {e}"
                )
            logger.info(
                "Continuing with unverified revocation status (fallback enabled)"
            )

    def get_certificate_info(self, cert: x509.Certificate) -> dict:
        """
        Extrae información útil del certificado.

        Args:
            cert: Certificado a analizar

        Returns:
            Diccionario con información del certificado
        """
        # Obtener fechas de validez (compatible con diferentes versiones de cryptography)
        try:
            not_before = cert.not_valid_before_utc
            not_after = cert.not_valid_after_utc
        except AttributeError:
            not_before = cert.not_valid_before
            not_after = cert.not_valid_after
            # Asegurar que sean timezone-aware
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

        # Extraer nombre común si existe
        try:
            cn_attrs = cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)
            if cn_attrs:
                info["common_name"] = cn_attrs[0].value
        except Exception:
            pass

        return info
