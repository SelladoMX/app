"""Cliente TSA para sellado de tiempo"""
import hashlib
import logging
from typing import Optional

import requests
from pyhanko.sign import timestamps

from ..config import TSA_URL, TSA_TIMEOUT
from ..errors import TSAError

logger = logging.getLogger(__name__)


class TSAClient:
    """Cliente para servicios de sellado de tiempo (TSA)"""

    def __init__(self, tsa_url: str = TSA_URL, timeout: int = TSA_TIMEOUT):
        """
        Inicializa el cliente TSA.

        Args:
            tsa_url: URL del servicio TSA
            timeout: Timeout en segundos para las peticiones
        """
        self.tsa_url = tsa_url
        self.timeout = timeout
        logger.info(f"TSA client initialized with URL: {tsa_url}")

    def get_timestamper(self) -> timestamps.HTTPTimeStamper:
        """
        Obtiene un timestamper configurado para pyhanko.

        Returns:
            Instancia de HTTPTimeStamper lista para usar

        Raises:
            TSAError: Si no se puede conectar al servicio TSA
        """
        try:
            return timestamps.HTTPTimeStamper(
                self.tsa_url,
                timeout=self.timeout
            )
        except Exception as e:
            logger.error(f"Error creating timestamper: {e}")
            raise TSAError(f"No se pudo crear el timestamper: {e}")

    def test_connection(self) -> bool:
        """
        Prueba la conexión con el servicio TSA.

        Returns:
            True si la conexión es exitosa, False en caso contrario
        """
        try:
            response = requests.head(
                self.tsa_url,
                timeout=self.timeout,
                allow_redirects=True
            )
            success = response.status_code < 500
            if success:
                logger.info("TSA connection test successful")
            else:
                logger.warning(f"TSA connection test failed with status {response.status_code}")
            return success
        except requests.RequestException as e:
            logger.warning(f"TSA connection test failed: {e}")
            return False
