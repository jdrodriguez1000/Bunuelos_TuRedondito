import pytest
import pandas as pd
import numpy as np
from unittest.mock import MagicMock, patch, mock_open
from src.ingestor import UnifiedIngestor, backoff_retry

@pytest.fixture
def mock_config():
    return {
        'bronze': {'path': 'data/test_bronze'},
        'ingestion': {
            'scoring': {
                'weights': {
                    'business_rules': 0.5,
                    'time_continuity': 0.2,
                    'data_integrity': 0.2,
                    'data_cleaning': 0.1
                },
                'penalties': {
                    'null_penalty_factor': 0.5,
                    'invalid_date_penalty': 20
                }
            },
            'tables': {
                'inventory': {'frequency': 'D'}
            }
        },
        'contract': {'path': 'contracts/data_contract.yaml'},
        'validation': {}
    }

@patch('src.ingestor.DBConnector')
@patch('src.ingestor.DataValidator')
@patch('os.makedirs')
def test_ingestor_initialization(mock_makedirs, mock_validator, mock_db_connector, mock_config):
    # Setup
    mock_db_instance = mock_db_connector.return_value
    mock_db_instance.get_config.return_value = mock_config
    
    # Act
    ingestor = UnifiedIngestor()
    
    # Assert
    assert ingestor.bronze_path == 'data/test_bronze'
    mock_makedirs.assert_called_once_with('data/test_bronze', exist_ok=True)
    assert ingestor.ingestion_config == mock_config['ingestion']['tables']

def test_calculate_null_pct():
    ingestor = MagicMock(spec=UnifiedIngestor)
    df = pd.DataFrame({
        'A': [1, None, 3, None],
        'B': [1, 2, 3, 4]
    })
    
    # We call the real method on the mock if we want, or just test the logic
    # Better: use a dummy instance but mock the __init__
    with patch.object(UnifiedIngestor, '__init__', return_value=None):
        ingestor = UnifiedIngestor()
        pct = ingestor._calculate_null_pct(df)
        assert pct == 25.0  # 2 nulls out of 8 values

def test_check_sentinels():
    with patch.object(UnifiedIngestor, '__init__', return_value=None):
        ingestor = UnifiedIngestor()
        df = pd.DataFrame({
            'A': [1, -999, 3, 'NULL_VAL'],
            'B': [1, 2, 3, 4]
        })
        sentinels = ingestor._check_sentinels(df, [-999, 'NULL_VAL'])
        # La respuesta es un Dict[ColName, Count]
        assert sentinels['A'] == 2
        assert 'B' not in sentinels

def test_analyze_time_series_invalid_dates():
    with patch.object(UnifiedIngestor, '__init__', return_value=None):
        ingestor = UnifiedIngestor()
        df = pd.DataFrame({
            'date_col': ['2023-01-01', 'not-a-date', '2023-01-02']
        })
        
        analysis = ingestor._analyze_time_series(df, 'D')
        
        assert analysis['invalid_dates_count'] == 1
        assert analysis['freshness_lag_days'] > 0 # Against 'now'

def test_backoff_retry_logic():
    mock_func = MagicMock()
    mock_func.side_effect = [Exception("Error1"), Exception("Error2"), "Success"]
    
    @backoff_retry(retries=3, backoff_factor=0.1)
    def test_call():
        return mock_func()
    
    result = test_call()
    assert result == "Success"
    assert mock_func.call_count == 3

def test_backoff_retry_exhausted():
    mock_func = MagicMock()
    mock_func.side_effect = Exception("Persistent Error")
    
    @backoff_retry(retries=2, backoff_factor=0.1)
    def test_call():
        return mock_func()
    
    with pytest.raises(Exception, match="Persistent Error"):
        test_call()
    assert mock_func.call_count == 2
