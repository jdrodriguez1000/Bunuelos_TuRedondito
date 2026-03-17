import pytest
import pandas as pd
import yaml
from unittest.mock import patch, MagicMock, mock_open
from src.ingestor import UnifiedIngestor

@pytest.fixture
def mock_dependencies():
    with patch('src.ingestor.DBConnector') as mock_db, \
         patch('src.ingestor.DataValidator') as mock_val, \
         patch('src.ingestor.subprocess.run') as mock_run:
        
        # Mock DB Client
        client = MagicMock()
        mock_db.get_service_client.return_value = client
        
        # Mock Config
        mock_config = {
            'ingestion': {
                'bronze_path': 'data/bronze',
                'checkpoint_tolerance_days': 1
            },
            'governance': {
                'weights': {'business_rules': 0.5, 'time_continuity': 0.2, 'data_integrity': 0.2, 'data_cleaning': 0.1},
                'penalties': {'per_null_pct': 5, 'per_invalid_date': 10}
            },
            'sources': {
                'test_table': {
                    'frequency': 'D',
                    'sentinels': [-999]
                }
            }
        }
        
        yield mock_db, mock_val, client, mock_config, mock_run

def test_hito_0_bootstrap_flow(mock_dependencies):
    mock_db, mock_val, client, mock_config, mock_run = mock_dependencies
    
    # Init Ingestor first
    with patch('src.ingestor.yaml.safe_load', return_value=mock_config), \
         patch('src.ingestor.os.makedirs'):
        
        ingestor = UnifiedIngestor()
        
        # Simular Hito 0: Tabla sys_validation_contract vacía
        mock_execute = MagicMock()
        mock_execute.data = []
        mock_execute.count = 100 
        
        # Estrategia de Mock Circular para Fluent API: 
        # Todos los métodos de filtrado devuelven el mismo objeto 'query'
        mock_query = ingestor.service_client.table.return_value.select.return_value
        for method in ['order', 'limit', 'eq', 'range']:
            getattr(mock_query, method).return_value = mock_query
        
        mock_query.execute.return_value = mock_execute
        
        # Mock DataValidator success
        mock_val.return_value.validate_table.return_value = (True, "Validación Exitosa")
        
        # Simular que solo hay una tabla en el contrato
        mock_contract = {
            'data_sources': [{'name': 'test_table', 'db_table': 'test_table', 'enabled': True}]
        }
        
        # EJECUCIÓN
        # Nota: side_effect ahora solo devuelve el contrato, ya que el config se cargó en el __init__
        with patch("builtins.open", mock_open(read_data="...")), \
             patch('src.ingestor.yaml.safe_load', return_value=mock_contract), \
             patch.object(ingestor, '_fetch_all_data', return_value=pd.DataFrame([{'a':1}])) as mock_fetch, \
             patch.object(ingestor, '_log_audit') as mock_log:
            
            ingestor.run_full_ingestion(execution_id="exec_123")
            
            # VERIFICACIÓN
            assert mock_fetch.called, "Debería haber llamado a _fetch_all_data en modo Bootstrap"
            assert mock_log.called, "Debería haber registrado auditoría"

def test_recovery_mode_when_invalid_contract(mock_dependencies):
    mock_db, mock_val, client, mock_config, mock_run = mock_dependencies
    
    # Init Ingestor first
    with patch('src.ingestor.yaml.safe_load', return_value=mock_config), \
         patch('src.ingestor.os.makedirs'):
        
        ingestor = UnifiedIngestor()
        
        # Simular que el contrato está marcado como INVALID en la DB (para forzar Modo Recuperación)
        mock_res = MagicMock()
        mock_res.data = [{'status': 'INVALID', 'version': '1.0.0'}]
        ingestor.service_client.table.return_value.select.return_value.order.return_value.limit.return_value.execute.return_value = mock_res
        
        mock_contract = {
            'data_sources': [{'name': 'test_table', 'db_table': 'test_table', 'enabled': True}]
        }
        
        # EJECUCIÓN
        with patch("builtins.open", mock_open(read_data="...")), \
             patch('src.ingestor.yaml.safe_load', return_value=mock_contract), \
             patch.object(ingestor, '_get_last_audit_state', return_value=None), \
             patch.object(ingestor, '_get_remote_count', return_value=100), \
             patch.object(ingestor, '_fetch_all_data', return_value=pd.DataFrame([{'a':1}])) as mock_fetch, \
             patch.object(ingestor, '_log_audit') as mock_log:
             
            ingestor.run_full_ingestion(execution_id="exec_456")
            
            # VERIFICACIÓN: En modo recuperación, SÍ procede para intentar sanar el sistema
            assert mock_fetch.called, "SÍ debería llamar a _fetch_all_data en modo Recuperación"
            assert mock_log.called, "SÍ debería registrar auditoría para intentar sanar el contrato"
