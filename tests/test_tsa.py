"""Tests para TSAClient"""
import pytest

from selladomx.signing.tsa import TSAClient
from selladomx.config import TSA_URL


class TestTSAClient:
    """Tests para cliente TSA"""

    def test_initialization(self):
        """Test inicialización básica"""
        client = TSAClient()
        assert client.primary_url == TSA_URL

    def test_custom_url(self):
        """Test con URL personalizada"""
        custom_url = "https://example.com/tsa"
        client = TSAClient(tsa_url=custom_url)
        assert client.primary_url == custom_url

    def test_get_timestamper(self):
        """Test obtención de timestamper"""
        client = TSAClient()
        timestamper = client.get_timestamper()
        assert timestamper is not None

    @pytest.mark.network
    def test_connection(self):
        """Test de conexión al TSA (requiere red)"""
        client = TSAClient()
        # Este test puede fallar si FreeTSA está caído
        # En producción, usarías pytest.mark.skipif
        result = client.test_connection()
        assert isinstance(result, bool)
