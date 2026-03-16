import pytest
from src.ingestor import UnifiedIngestor
from src.connector.db_connector import DBConnector

@pytest.mark.integration
def test_supabase_connectivity():
    """Prueba básica de conectividad con Supabase (Solo lectura)."""
    connector = DBConnector()
    client = connector.get_service_client()
    
    # Intentar una consulta simple a una tabla de sistema que sabemos que existe
    try:
        res = client.table("sys_pipeline_execution").select("count", count="exact").limit(1).execute()
        assert res.count is not None
    except Exception as e:
        pytest.fail(f"Fallo de conexión a Supabase: {str(e)}")

@pytest.mark.integration
def test_ingestor_remote_count():
    """Verifica que el ingestor pueda obtener conteos de tablas reales."""
    ingestor = UnifiedIngestor()
    # Usamos la tabla de inventario que sabemos que existe
    count = ingestor._get_remote_count("usr_inventario_detallado")
    assert isinstance(count, int)
    assert count >= 0

@pytest.mark.integration
def test_ingestor_last_audit_state():
    """Verifica la recuperación del último estado de auditoría."""
    ingestor = UnifiedIngestor()
    state = ingestor._get_last_audit_state("usr_inventario_detallado")
    
    # Puede ser None si nunca se ha auditado, pero si existe debe tener campos mínimos
    if state:
        assert 'row_count' in state
        assert 'semantic_hash' in state
