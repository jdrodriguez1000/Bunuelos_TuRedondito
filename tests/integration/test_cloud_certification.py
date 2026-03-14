import pytest
from unittest.mock import MagicMock, patch
from src.connector.cloud_certification import CloudCertifier

@pytest.fixture
def mock_db_connector():
    with patch('src.connector.cloud_certification.DBConnector') as mock_cls:
        mock_instance = mock_cls.return_value
        mock_instance.get_config.return_value = {
            "paths": {
                "cloud_storage": {
                    "s3_tickets_prefix": "stage_load",
                    "s3_ticket_name": "load_report.json"
                }
            }
        }
        mock_instance.s3_config = {"bucket": "test-bucket"}
        yield mock_instance

def test_publish_ticket_success(mock_db_connector):
    # Arrange
    # Mocking the client structure: client.storage.from_().upload()
    mock_client = MagicMock()
    mock_db_connector.get_service_client.return_value = mock_client
    
    mock_storage_bucket = MagicMock()
    mock_client.storage.from_.return_value = mock_storage_bucket
    
    # Act
    certifier = CloudCertifier()
    report = {"execution_id": "test_123", "status": "SUCCESS"}
    cloud_path = certifier.publish_ticket(report)
    
    # Assert
    assert "stage_load" in cloud_path
    assert "load_report.json" in cloud_path
    mock_client.storage.from_.assert_called_with("test-bucket")
    mock_storage_bucket.upload.assert_called()

def test_publish_ticket_failure_logic(mock_db_connector):
    # Arrange
    mock_client = MagicMock()
    mock_db_connector.get_service_client.return_value = mock_client
    
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
