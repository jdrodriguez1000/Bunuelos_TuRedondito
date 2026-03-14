import pytest
import os
from dotenv import load_dotenv
from src.connector.db_connector import DBConnector
from supabase import Client

load_dotenv()

def test_singleton_identity():
    """
    Verifica que DBConnector sea un Singleton real (misma instancia en memoria).
    Trazabilidad: [ARC-07], [REQ-CON-01]
    """
    conn1 = DBConnector()
    conn2 = DBConnector()
    assert conn1 is conn2
    assert id(conn1) == id(conn2)

def test_clients_types():
    """Verifica que los métodos retornen instancias válidas de Supabase Client."""
    connector = DBConnector()
    client = connector.get_client()
    admin_client = connector.get_service_client()
    
    assert isinstance(client, Client)
    assert isinstance(admin_client, Client)

@pytest.mark.skipif(not os.getenv("SUPABASE_URL"), reason="No hay credenciales reales para Integration Test")
def test_real_handshake():
    """
    Valida la conexión real con Supabase si las credenciales están presentes.
    Trazabilidad: [REQ-VAL-01], [MET-INF-01]
    """
    connector = DBConnector()
    assert connector.test_connection() is True

def test_s3_config_loading():
    """
    Verifica que la configuración de S3 se cargue correctamente en el objeto.
    Trazabilidad: [REQ-S3-01]
    """
    connector = DBConnector()
    s3 = connector.s3_config
    
    assert "endpoint" in s3
    assert "bucket" in s3
    assert "access_key" in s3
    assert "secret_key" in s3
    # Verificamos que no sean nulos si las env vars están presentes
    if os.getenv("SUPABASE_S3_ENDPOINT"):
        assert s3["endpoint"] == os.getenv("SUPABASE_S3_ENDPOINT")
