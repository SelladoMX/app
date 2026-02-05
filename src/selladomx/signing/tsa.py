"""Cliente TSA para sellado de tiempo"""
import hashlib
import logging
from typing import Optional

import requests
from pyhanko.sign import timestamps

from ..config import TSA_URL, TSA_TIMEOUT, TSA_FREE_PROVIDERS
from ..errors import TSAError

logger = logging.getLogger(__name__)


class TSAClient:
    """Cliente para servicios de sellado de tiempo (TSA) con soporte multi-provider y fallback"""

    def __init__(
        self,
        tsa_url: Optional[str] = None,
        timeout: int = TSA_TIMEOUT,
        enable_fallback: bool = True
    ):
        """
        Inicializa el cliente TSA.

        Args:
            tsa_url: URL del servicio TSA (None = usar lista de providers con fallback)
            timeout: Timeout en segundos para las peticiones
            enable_fallback: Si True, intenta fallback a otros TSAs en caso de falla
        """
        self.primary_url = tsa_url or TSA_URL
        self.timeout = timeout
        self.enable_fallback = enable_fallback
        self.fallback_providers = TSA_FREE_PROVIDERS if enable_fallback else [self.primary_url]
        logger.info(f"TSA client initialized with primary URL: {self.primary_url}")
        if enable_fallback:
            logger.info(f"Fallback enabled with {len(self.fallback_providers)} providers")

    def get_timestamper(self) -> timestamps.HTTPTimeStamper:
        """
        Obtiene un timestamper configurado para pyhanko con fallback automático.

        Returns:
            Instancia de HTTPTimeStamper lista para usar

        Raises:
            TSAError: Si ningún servicio TSA está disponible
        """
        last_error = None

        for tsa_url in self.fallback_providers:
            try:
                logger.info(f"Attempting to create timestamper with: {tsa_url}")
                timestamper = timestamps.HTTPTimeStamper(
                    tsa_url,
                    timeout=self.timeout
                )
                logger.info(f"Successfully created timestamper with: {tsa_url}")
                return timestamper
            except Exception as e:
                last_error = e
                logger.warning(f"Failed to create timestamper with {tsa_url}: {e}")
                continue

        # Si llegamos aquí, todos los TSAs fallaron
        logger.error(f"All TSA providers failed. Last error: {last_error}")
        raise TSAError(
            f"No se pudo conectar a ningún servicio TSA. "
            f"Intentamos {len(self.fallback_providers)} proveedores. "
            f"Último error: {last_error}"
        )

    def test_connection(self, url: Optional[str] = None) -> bool:
        """
        Prueba la conexión con el servicio TSA.

        Args:
            url: URL a probar (None = usar primary_url)

        Returns:
            True si la conexión es exitosa, False en caso contrario
        """
        test_url = url or self.primary_url
        try:
            response = requests.head(
                test_url,
                timeout=self.timeout,
                allow_redirects=True
            )
            success = response.status_code < 500
            if success:
                logger.info(f"TSA connection test successful for {test_url}")
            else:
                logger.warning(f"TSA connection test failed for {test_url} with status {response.status_code}")
            return success
        except requests.RequestException as e:
            logger.warning(f"TSA connection test failed for {test_url}: {e}")
            return False

    def test_all_providers(self) -> dict[str, bool]:
        """
        Prueba la conexión con todos los proveedores TSA disponibles.

        Returns:
            Diccionario con URL del TSA como key y resultado del test como value
        """
        results = {}
        for tsa_url in self.fallback_providers:
            results[tsa_url] = self.test_connection(tsa_url)
        return results
