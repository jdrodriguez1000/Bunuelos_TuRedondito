import pytest
from unittest.mock import MagicMock, patch
from src.connector.cloud_certification import CloudCertifier

@pytest.fixture
def mock_supabase():
    with patch('src.connector.db_connector.DBConnector.get_service_client') as mock:
        yield mock

def test_publish_ticket_success(mock_supabase):
    # Arrange
    # Mocking the client structure: client.storage.from_().upload()
    mock_client = MagicMock()
    mock_supabase.return_value = mock_client
    
    mock_storage_bucket = MagicMock()
    mock_client.storage.from_.return_value = mock_storage_bucket
    
    # Act
    certifier = CloudCertifier()
    report = {"execution_id": "test_123", "status": "SUCCESS"}
    cloud_path = certifier.publish_ticket(report)
    
    # Assert
    assert "stage_load" in cloud_path
    assert "load_report.json" in cloud_path
    mock_client.storage.from_.assert_called_with(certifier.bucket_name)
    mock_storage_bucket.upload.assert_called()

def test_publish_ticket_failure_logic(mock_supabase):
    # Arrange
    mock_client = MagicMock()
    mock_supabase.return_value = mock_client
    
    mock_storage_bucket = MagicMock()
    mock_client.storage.from_.return_value = mock_storage_bucket
    
    # Simulate first upload failure to test the 'remove + upload' fallback
    # Some older versions or specific error codes might trigger this
    mock_storage_bucket.upload.side_effect = [Exception("Upload failed"), MagicMock()]
    
    # Act
    certifier = CloudCertifier()
    report = {"execution_id": "test_456"}
    cloud_path = certifier.publish_ticket(report)
    
    # Assert
    assert "load_report.json" in cloud_path
    assert mock_storage_bucket.remove.called
    assert mock_storage_bucket.upload.call_count == 2
