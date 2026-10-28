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


class CertificatePasswordError(CertificateError):
    """La contraseña de la clave privada es incorrecta o falta"""

    pass


class CertificateKeyMismatchError(CertificateError):
    """La clave privada no corresponde al certificado"""

    pass


class SigningError(SelladoMXError):
    """Error al firmar PDF"""

    pass


class TSAError(SelladoMXError):
    """Error con el servicio de sellado de tiempo (TSA)"""

    default_message = "No se pudo obtener el sello de tiempo."

    def __init__(self, message: str | None = None):
        super().__init__(message or self.default_message)


class TSAUnavailableError(TSAError):
    """Ningún proveedor TSA fue alcanzable (red, proxy o antivirus)"""

    default_message = (
        "No pudimos conectar con ningún servicio de sellado de tiempo. "
        "Revisa tu conexión, proxy o antivirus (protección web)."
    )


class TSATimeoutError(TSAUnavailableError):
    """Todos los proveedores TSA tardaron demasiado en responder"""

    default_message = (
        "Los servicios de sellado de tiempo tardaron demasiado en responder. "
        "Revisa tu conexión e inténtalo de nuevo."
    )


class TSAResponseError(TSAError):
    """El servidor TSA rechazó la solicitud o respondió con datos no válidos"""

    default_message = (
        "El servicio de sellado de tiempo rechazó la solicitud o envió una "
        "respuesta no válida. Inténtalo de nuevo más tarde."
    )


class PDFError(SelladoMXError):
    """Error al procesar PDF"""

    pass
