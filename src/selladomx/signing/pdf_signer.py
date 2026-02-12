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
from pyhanko.pdf_utils.reader import PdfFileReader
from pyhanko.sign import fields, signers
from pyhanko.sign.validation import validate_pdf_signature

from ..config import SIGNED_SUFFIX
from ..errors import PDFError, SigningError
from .certificate_validator import PrivateKey
from .tsa import TSAClient

logger = logging.getLogger(__name__)


class PDFSigner:
    """Firmador de PDFs con certificados digitales"""

    def __init__(
        self,
        cert: x509.Certificate,
        private_key: PrivateKey,
        tsa_client: Optional[TSAClient] = None,
    ):
        """
        Inicializa el firmador de PDFs.

        Args:
            cert: Certificado digital
            private_key: Clave privada correspondiente
            tsa_client: Cliente TSA opcional para sellado de tiempo
        """
        self.cert = cert
        self.private_key = private_key
        self.tsa_client = tsa_client
        logger.info("PDF signer initialized")

    def sign_pdf(self, pdf_path: Path, output_path: Optional[Path] = None) -> Path:
        """
        Firma un PDF con el certificado digital.

        Args:
            pdf_path: Ruta al PDF a firmar
            output_path: Ruta del PDF firmado (opcional, por defecto agrega sufijo)

        Returns:
            Ruta al PDF firmado

        Raises:
            PDFError: Si hay un error leyendo el PDF
            SigningError: Si hay un error al firmar
        """
        pdf_path = Path(pdf_path)

        if not pdf_path.exists():
            raise PDFError(f"Archivo PDF no encontrado: {pdf_path}")

        # Determinar ruta de salida
        if output_path is None:
            output_path = (
                pdf_path.parent / f"{pdf_path.stem}{SIGNED_SUFFIX}{pdf_path.suffix}"
            )
        else:
            output_path = Path(output_path)

        logger.info(f"Signing PDF: {pdf_path.name}")

        try:
            # Leer PDF en memoria
            with open(pdf_path, "rb") as f:
                pdf_data = BytesIO(f.read())

            # Crear writer incremental (preserva PDF original)
            writer = IncrementalPdfFileWriter(pdf_data)

            # Convertir certificado de cryptography a asn1crypto
            cert_bytes = self.cert.public_bytes(encoding=serialization.Encoding.DER)
            asn1_cert = asn1_x509.Certificate.load(cert_bytes)

            # Convertir clave privada de cryptography a asn1crypto
            key_bytes = self.private_key.private_bytes(
                encoding=serialization.Encoding.DER,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )
            asn1_key = asn1_keys.PrivateKeyInfo.load(key_bytes)

            # Crear signer con objetos asn1crypto
            signer = signers.SimpleSigner(
                signing_cert=asn1_cert, signing_key=asn1_key, cert_registry=None
            )

            # Configurar metadata de la firma
            signature_meta = signers.PdfSignatureMetadata(
                field_name="Signature1",
                name=self._get_signer_name(),
                location="México",
            )

            # Agregar campo de firma invisible
            fields.append_signature_field(
                writer,
                sig_field_spec=fields.SigFieldSpec(
                    sig_field_name=signature_meta.field_name,
                    box=None,  # Sin sello visual
                ),
            )

            # Obtener timestamper si está disponible
            timestamper = None
            if self.tsa_client:
                try:
                    timestamper = self.tsa_client.get_timestamper()
                    logger.info("Using TSA for timestamp")
                except Exception as e:
                    logger.warning(
                        f"Could not get timestamper, continuing without it: {e}"
                    )

            # Firmar el PDF
            out = signers.sign_pdf(
                writer,
                signature_meta=signature_meta,
                signer=signer,
                timestamper=timestamper,
                in_place=True,
            )

            # Guardar PDF firmado
            with open(output_path, "wb") as f:
                f.write(out.getbuffer())

            logger.info(f"PDF signed successfully: {output_path.name}")
            return output_path

        except Exception as e:
            logger.error(f"Error signing PDF: {e}")
            raise SigningError(f"No se pudo firmar el PDF: {e}")

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
        Verifica las firmas de un PDF.

        Args:
            pdf_path: Ruta al PDF firmado

        Returns:
            True si todas las firmas son válidas

        Raises:
            PDFError: Si hay un error leyendo el PDF
        """
        pdf_path = Path(pdf_path)

        if not pdf_path.exists():
            raise PDFError(f"Archivo PDF no encontrado: {pdf_path}")

        try:
            with open(pdf_path, "rb") as f:
                reader = PdfFileReader(f)
                sig_fields = fields.enumerate_sig_fields(reader)

                # Verificar cada firma
                all_valid = True
                for sig_field in sig_fields:
                    logger.info(f"Verifying signature field: {sig_field.field_name}")

                    embedded_sig = sig_field.sig_object
                    if embedded_sig is None:
                        logger.warning(
                            f"Signature field {sig_field.field_name} has no signature"
                        )
                        all_valid = False
                        continue

                    # Validar firma
                    try:
                        status = validate_pdf_signature(embedded_sig, reader)
                        if status.valid:
                            logger.info(f"Signature {sig_field.field_name} is valid")
                        else:
                            logger.warning(
                                f"Signature {sig_field.field_name} is invalid"
                            )
                            all_valid = False
                    except Exception as e:
                        logger.error(
                            f"Error validating signature {sig_field.field_name}: {e}"
                        )
                        all_valid = False

                return all_valid

        except Exception as e:
            logger.error(f"Error verifying PDF signatures: {e}")
            raise PDFError(f"No se pudo verificar las firmas del PDF: {e}")
