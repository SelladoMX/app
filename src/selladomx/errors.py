"""Excepciones personalizadas"""


class SelladoMXError(Exception):
    """Excepción base"""

    pass


class CertificateError(SelladoMXError):
    """Error relacionado con certificados"""

    pass


class CertificateExpiredError(CertificateError):
    """Certificado expirado"""

    pass


class CertificateRevokedError(CertificateError):
    """Certificado revocado"""

    pass


class CertificateValidationError(CertificateError):
    """Error al validar certificado"""

    pass


class SigningError(SelladoMXError):
    """Error al firmar PDF"""

    pass


class TSAError(SelladoMXError):
    """Error con el servicio TSA"""

    pass


class PDFError(SelladoMXError):
    """Error al procesar PDF"""

    pass
