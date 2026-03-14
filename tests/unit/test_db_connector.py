import pytest
from unittest.mock import patch, MagicMock
import os
from src.connector.db_connector import DBConnector
from supabase import Client

# Fixture para resetear el Singleton entre tests y evitar contaminación
@pytest.fixture(autouse=True)
def reset_singleton():
    DBConnector._instance = None
    yield
    DBConnector._instance = None

# Mock global para variables de entorno requeridas por el inicializador
@pytest.fixture
def mock_env():
    with patch.dict(os.environ, {
        "SUPABASE_URL": "https://dummy.supabase.co",
        "SUPABASE_KEY": "dummy-key",
        "SUPABASE_SERVICE_ROLE_KEY": "dummy-admin-key",
        "SUPABASE_S3_ENDPOINT": "https://dummy.s3.com",
        "SUPABASE_S3_ACCESS_KEY_ID": "dummy-access",
        "SUPABASE_S3_SECRET_ACCESS_KEY": "dummy-secret",
        "SUPABASE_S3_REGION": "us-east-1",
        "SUPABASE_S3_BUCKET": "dummy-bucket"
    }):
        yield

def test_singleton_identity(mock_env):
    """
    Verifica que DBConnector sea un Singleton real (misma instancia en memoria).
    Trazabilidad: [ARC-07], [REQ-CON-01]
    """
    conn1 = DBConnector()
    conn2 = DBConnector()
    assert conn1 is conn2
    assert id(conn1) == id(conn2)

def test_clients_types(mock_env):
    """Verifica que los métodos retornen instancias válidas de Supabase Client."""
    # Mockeamos create_client para evitar llamadas reales a red en unit test
    with patch('src.connector.db_connector.create_client') as mock_create:
        mock_create.return_value = MagicMock(spec=Client)
        connector = DBConnector()
        client = connector.get_client()
        admin_client = connector.get_service_client()
        
        assert client is not None
        assert admin_client is not None

@pytest.mark.skipif(not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_S3_ENDPOINT"), 
                    reason="No hay credenciales reales completas para Integration Test")
def test_real_handshake():
    """
    Valida la conexión real con Supabase si las credenciales están presentes.
    Trazabilidad: [REQ-VAL-01], [MET-INF-01]
    """
    connector = DBConnector()
    assert connector.test_connection() is True

def test_s3_config_loading(mock_env):
    """
    Verifica que la configuración de S3 se cargue correctamente en el objeto.
    Trazabilidad: [REQ-S3-01]
    """
    with patch('src.connector.db_connector.create_client'):
        connector = DBConnector()
        s3 = connector.s3_config
        
        assert s3["endpoint"] == "https://dummy.s3.com"
        assert s3["bucket"] == "dummy-bucket"
        assert s3["access_key"] == "dummy-access"
        assert s3["secret_key"] == "dummy-secret"
