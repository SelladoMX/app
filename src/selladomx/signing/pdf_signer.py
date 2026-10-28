"""Core de firma de PDFs con pyhanko"""

import logging
from io import BytesIO
from pathlib import Path
from typing import Optional

from asn1crypto import keys as asn1_keys
from asn1crypto import x509 as asn1_x509
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.pdf_utils.misc import PdfReadError
from pyhanko.pdf_utils.reader import PdfFileReader
from pyhanko.sign import fields, signers
from pyhanko.sign.timestamps import TimeStamper
from pyhanko.sign.validation import validate_pdf_signature

from ..api.exceptions import APIError
from ..config import SIGNED_SUFFIX
from ..errors import PDFError, SelladoMXError, SigningError
from .certificate_validator import PrivateKey
from .tsa import TSAClient

logger = logging.getLogger(__name__)

# Hex characters reserved for the CMS in /Contents (2 per DER byte). Passing it
# makes pyhanko skip its size estimation, which would request a throwaway
# timestamp over the network. Measured CMS with an RSA-2048 SAT-like cert
# (1.8 KB): 7.9 KB (freetsa), 9.3 KB (DigiCert), 9.4 KB (Certum), 9.9 KB
# (Sectigo). 20 KB is twice the largest, because overflowing after the
# professional timestamp is issued would waste the credit.
SIGNATURE_BYTES_RESERVED = 40960

MAX_OUTPUT_NAME_ATTEMPTS = 1000


def signed_output_path(pdf_path: Path, output_dir: Optional[Path] = None) -> Path:
    """
    Returns a path for the signed copy that doesn't overwrite an existing file.

    Args:
        pdf_path: PDF to sign
        output_dir: Destination folder (None = the PDF's folder)

    Returns:
        ``<stem>_firmado.pdf``, or ``<stem>_firmado (N).pdf`` if taken

    Raises:
        PDFError: If every name up to ``MAX_OUTPUT_NAME_ATTEMPTS`` is taken
    """
    pdf_path = Path(pdf_path)
    folder = Path(output_dir) if output_dir else pdf_path.parent
    base = f"{pdf_path.stem}{SIGNED_SUFFIX}"
    candidate = folder / f"{base}{pdf_path.suffix}"
    for counter in range(1, MAX_OUTPUT_NAME_ATTEMPTS + 1):
        if not candidate.exists():
            return candidate
        candidate = folder / f"{base} ({counter}){pdf_path.suffix}"
    logger.error(f"No free output name for {pdf_path.name}")
    raise PDFError(
        f"Ya existen demasiadas copias firmadas de {pdf_path.name} en la carpeta "
        "de destino. Mueve o borra algunas e inténtalo de nuevo."
    )


class PDFSigner:
    """Firmador de PDFs con certificados digitales"""

    def __init__(
        self,
        cert: x509.Certificate,
        private_key: PrivateKey,
        tsa_client: Optional[TSAClient] = None,
        timestamper: Optional[TimeStamper] = None,
    ):
        """
        Inicializa el firmador de PDFs.

        Args:
            cert: Certificado digital
            private_key: Clave privada correspondiente
            tsa_client: Cliente TSA opcional para sellado de tiempo (free)
            timestamper: Pre-built pyhanko TimeStamper (e.g., APITimeStamper for professional TSA)
        """
        self.cert = cert
        self.private_key = private_key
        self.tsa_client = tsa_client
        self.timestamper = timestamper
        logger.info("PDF signer initialized")

    def sign_pdf(self, pdf_path: Path, output_path: Optional[Path] = None) -> Path:
        """
        Firma un PDF con el certificado digital.

        Args:
            pdf_path: Ruta al PDF a firmar
            output_path: Ruta del PDF firmado (opcional; por defecto agrega el
                sufijo sin sobrescribir un archivo existente)

        Returns:
            Ruta al PDF firmado

        Raises:
            PDFError: Si hay un error leyendo o guardando el PDF
            TSAError: Si no se pudo obtener el sello de tiempo
            APIError: Errores del API en el sellado profesional
            SigningError: Si hay cualquier otro error al firmar
        """
        pdf_path = Path(pdf_path)

        if not pdf_path.exists():
            raise PDFError(f"Archivo PDF no encontrado: {pdf_path.name}")

        if output_path is None:
            output_path = signed_output_path(pdf_path)
        else:
            output_path = Path(output_path)

        logger.info(f"Signing PDF: {pdf_path.name}")

        # Created before signing so that an unwritable folder fails before a
        # professional timestamp spends a credit
        try:
            output_file = open(output_path, "xb")
        except OSError as e:
            logger.error(f"Could not create {output_path.name}: {e.strerror}")
            raise PDFError(
                f"No se pudo guardar {output_path.name}. Revisa que la carpeta "
                "permita escribir y que el archivo no esté abierto en otro programa."
            ) from e

        try:
            with output_file:
                out = self._sign_to_buffer(pdf_path)
                output_file.write(out.getbuffer())
        except OSError as e:
            output_path.unlink(missing_ok=True)
            logger.error(f"Could not write {output_path.name}: {e.strerror}")
            raise PDFError(
                f"No se pudo guardar {output_path.name}. Revisa que la carpeta "
                "permita escribir y que el archivo no esté abierto en otro programa."
            ) from e
        except BaseException:
            output_path.unlink(missing_ok=True)
            raise

        logger.info(f"PDF signed successfully: {output_path.name}")
        return output_path

    def _sign_to_buffer(self, pdf_path: Path) -> BytesIO:
        """Firma ``pdf_path`` y devuelve el PDF firmado en memoria."""
        try:
            with open(pdf_path, "rb") as f:
                pdf_data = BytesIO(f.read())

            # Escritura incremental: preserva el PDF original. strict=False
            # porque Word y otros exportadores de Office generan tablas xref
            # híbridas, que pyhanko se niega a firmar en modo estricto.
            writer = IncrementalPdfFileWriter(pdf_data, strict=False)

            # pyhanko requiere objetos asn1crypto, no de cryptography
            cert_bytes = self.cert.public_bytes(encoding=serialization.Encoding.DER)
            asn1_cert = asn1_x509.Certificate.load(cert_bytes)

            key_bytes = self.private_key.private_bytes(
                encoding=serialization.Encoding.DER,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )
            asn1_key = asn1_keys.PrivateKeyInfo.load(key_bytes)

            signer = signers.SimpleSigner(
                signing_cert=asn1_cert, signing_key=asn1_key, cert_registry=None
            )

            signature_meta = signers.PdfSignatureMetadata(
                field_name="Signature1",
                name=self._get_signer_name(),
                location="México",
            )

            fields.append_signature_field(
                writer,
                sig_field_spec=fields.SigFieldSpec(
                    sig_field_name=signature_meta.field_name,
                    box=None,  # Sin sello visual
                ),
            )

            timestamper = self.timestamper
            if timestamper is None and self.tsa_client:
                timestamper = self.tsa_client.get_timestamper()
                logger.info("Using free TSA for timestamp")
            elif timestamper is not None:
                logger.info("Using provided timestamper (professional TSA)")

            out = signers.sign_pdf(
                writer,
                signature_meta=signature_meta,
                signer=signer,
                timestamper=timestamper,
                in_place=True,
                bytes_reserved=SIGNATURE_BYTES_RESERVED,
            )
        except (SelladoMXError, APIError):
            raise
        except PdfReadError as e:
            logger.error(f"Could not read {pdf_path.name}: {e}")
            raise PDFError(
                "No se pudo leer el PDF. Puede estar dañado o protegido con "
                "contraseña."
            ) from e
        except Exception as e:
            logger.error(f"Error signing {pdf_path.name}: {e!r}")
            raise SigningError(f"No se pudo firmar el PDF: {e}") from e

        return out

    def _get_signer_name(self) -> str:
        """Extrae el nombre del firmante del certificado"""
        try:
            cn_attrs = self.cert.subject.get_attributes_for_oid(
                x509.NameOID.COMMON_NAME
            )
            if cn_attrs:
                return cn_attrs[0].value
        except Exception:
            pass
        return "Firmante Digital"

    @staticmethod
    def verify_signature(pdf_path: Path) -> bool:
        """
        Verifica la integridad criptográfica de las firmas de un PDF.

        No valida la cadena de confianza ni la revocación del certificado.

        Args:
            pdf_path: Ruta al PDF firmado

        Returns:
            True si el PDF tiene al menos una firma y todas son íntegras y válidas

        Raises:
            PDFError: Si hay un error leyendo el PDF
        """
        pdf_path = Path(pdf_path)

        if not pdf_path.exists():
            raise PDFError(f"Archivo PDF no encontrado: {pdf_path.name}")

        try:
            with open(pdf_path, "rb") as f:
                reader = PdfFileReader(f, strict=False)
                embedded_sigs = reader.embedded_signatures
                if not embedded_sigs:
                    logger.info(f"No signatures found in {pdf_path.name}")
                    return False

                all_valid = True
                for embedded_sig in embedded_sigs:
                    name = embedded_sig.field_name
                    try:
                        status = validate_pdf_signature(embedded_sig)
                    except Exception as e:
                        logger.error(f"Error validating signature {name}: {e!r}")
                        all_valid = False
                        continue
                    if status.intact and status.valid:
                        logger.info(f"Signature {name} is valid")
                    else:
                        logger.warning(f"Signature {name} is invalid")
                        all_valid = False

                return all_valid

        except Exception as e:
            logger.error(f"Error verifying signatures of {pdf_path.name}: {e!r}")
            raise PDFError(f"No se pudo verificar las firmas del PDF: {e}") from e
