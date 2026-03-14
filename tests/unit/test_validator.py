import pytest
import pandas as pd
import json
from src.validator import DataValidator

@pytest.fixture
def validator_config():
    return {
        "thresholds": {
            "max_nat_increase_pct": 0.05
        },
        "fingerprint": {
            "algorithm": "sha256"
        }
    }

@pytest.fixture
def sample_df():
    data = {
        "fecha": ["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04"],
        "ventas": [10, 20, 15, 100],  # 100 is an outlier
        "categoria": ["A", "B", "A", "C"]
    }
    df = pd.DataFrame(data)
    df["fecha"] = pd.to_datetime(df["fecha"])
    return df

@pytest.fixture
def table_contract():
    return {
        "columns": {
            "fecha": {"type": "datetime"},
            "ventas": {"type": "int"},
            "categoria": {"type": "string"}
        }
    }

def test_numeric_profiling_and_outliers(validator_config, sample_df, table_contract):
    # Arrange
    validator = DataValidator(validator_config)
    
    # Act
    report = validator.validate_table("test_table", sample_df, table_contract)
    
    # Assert
    assert report["status"] == "VALID"
    ventas_stats = report["columns"]["ventas"]["stats"]
    assert ventas_stats["min"] == 10.0
    assert ventas_stats["max"] == 100.0
    assert "q1" in ventas_stats
    assert "median" in ventas_stats
    assert "q3" in ventas_stats
    
    outliers = report["columns"]["ventas"]["outliers"]
    assert outliers["count"] == 1  # 100 should be an outlier
    assert outliers["upper_bound"] < 100.0

def test_categorical_profiling(validator_config, sample_df, table_contract):
    # Arrange
    validator = DataValidator(validator_config)
    
    # Act
    report = validator.validate_table("test_table", sample_df, table_contract)
    
    # Assert
    cat_summary = report["columns"]["categoria"]["summary"]
    assert cat_summary["unique_values"] == 3
    assert "A" in cat_summary["top_frequencies"]
    assert cat_summary["top_frequencies"]["A"]["count"] == 2
    assert cat_summary["top_frequencies"]["A"]["percentage"] == 0.5

def test_missing_columns(validator_config, sample_df, table_contract):
    # Arrange
    validator = DataValidator(validator_config)
    df_missing = sample_df.drop(columns=["categoria"])
    
    # Act
    report = validator.validate_table("test_table", df_missing, table_contract)
    
    # Assert
    assert report["status"] == "INVALID"
    assert any("categoria" in err for err in report["errors"])

def test_semantic_hash_consistency(validator_config, sample_df, table_contract):
    # Arrange
    validator = DataValidator(validator_config)
    
    # Act
    report1 = validator.validate_table("test_table", sample_df, table_contract)
    report2 = validator.validate_table("test_table", sample_df, table_contract)
    
    # Assert
    assert report1["semantic_hash"] == report2["semantic_hash"]
    assert len(report1["semantic_hash"]) == 64  # SHA256 length
