import pytest
import yaml
import os

# Trazabilidad: [T-1.3-05], [RULE-QA]
# Objetivo: Validar la integridad y gobernanza del Contrato de Datos.

def load_contract():
    """Helper para cargar el contrato de datos."""
    contract_path = os.path.join(os.getcwd(), "contracts", "contracts", "data_contract.yaml")
    with open(contract_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def load_config():
    """Helper para cargar la configuración maestra."""
    config_path = os.path.join(os.getcwd(), "config.yaml")
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def test_contract_syntax():
    """Validación de sintaxis YAML y estructura raíz."""
    # Arrange & Act
    data = load_contract()
    
    # Assert
    assert data is not None, "El contrato no pudo ser cargado (está vacío o es inválido)."
    assert "data_sources" in data, "Falta la sección raíz 'data_sources' en el contrato."
    assert isinstance(data["data_sources"], list), "'data_sources' debe ser una lista."

def test_contract_mandatory_fields():
    """Valida que cada fuente tenga los campos técnicos mínimos obligatorios."""
    # Arrange
    data = load_contract()
    required_fields = ["name", "enabled", "db_table", "primary_key", "schema"]
    
    # Act & Assert
    for source in data["data_sources"]:
        for field in required_fields:
            assert field in source, f"Falta el campo obligatorio '{field}' en la fuente '{source.get('name', 'UNKNOWN')}'."

def test_contract_unique_names():
    """Asegura que no existan alias (nombres) duplicados en el contrato."""
    # Arrange
    data = load_contract()
    names = [s["name"] for s in data["data_sources"]]
    
    # Act & Assert
    assert len(names) == len(set(names)), f"Existen nombres de fuentes duplicados: {names}"

def test_contract_mandatory_source_registration():
    """
    Verifica que la fuente mandatoria definida en config.yaml esté registrada y habilitada.
    Trazabilidad: [BR-03-01], [CONFIG-CONTRACT]
    """
    # Arrange
    config = load_config()
    contract = load_contract()
    
    mandatory_name = config["contract"]["mandatory_source"]
    
    # Act
    sources = {s["name"]: s for s in contract["data_sources"]}
    
    # Assert
    assert mandatory_name in sources, f"La fuente obligatoria '{mandatory_name}' definida en config.yaml no existe en el contrato."
    assert sources[mandatory_name]["enabled"] is True, f"La fuente obligatoria '{mandatory_name}' debe estar habilitada (enabled: true)."

def test_contract_target_variable_registration():
    """
    Valida que la variable objetivo (target) esté presente en la fuente obligatoria.
    Trazabilidad: [DAT-03], [RE-1.3-01]
    """
    # Arrange
    config = load_config()
    contract = load_contract()
    
    mandatory_name = config["contract"]["mandatory_source"]
    target_var = config["contract"]["target_variable"]
    
    # Act
    sources = {s["name"]: s for s in contract["data_sources"]}
    mandatory_schema = sources[mandatory_name]["schema"]
    
    # Assert
    assert target_var in mandatory_schema, f"La variable target '{target_var}' no está registrada en el esquema de '{mandatory_name}'."

def test_contract_valid_types():
    """Verifica que los tipos de datos en el esquema sean compatibles con el motor de forecasting."""
    # Arrange
    data = load_contract()
    allowed_types = ["datetime", "int", "float", "string", "boolean"]
    
    # Act & Assert
    for source in data["data_sources"]:
        for col, col_type in source["schema"].items():
            assert col_type in allowed_types, f"Tipo '{col_type}' no permitido en columna '{col}' de fuente '{source['name']}'."

def test_contract_pk_integrity():
    """Asegura que la llave primaria definida exista dentro del esquema de la tabla."""
    # Arrange
    data = load_contract()
    
    # Act & Assert
    for source in data["data_sources"]:
        pk = source["primary_key"]
        schema_cols = source["schema"].keys()
        assert pk in schema_cols, f"La PK '{pk}' no existe en el esquema definido para '{source['name']}'."

def test_contract_db_table_mapping():
    """Valida que cada db_table del contrato esté registrada en la sección tables del config.yaml."""
    # Arrange
    config = load_config()
    contract = load_contract()
    
    allowed_db_tables = config["tables"].values()
    
    # Act & Assert
    for source in contract["data_sources"]:
        db_table = source["db_table"]
        assert db_table in allowed_db_tables, f"La tabla técnica '{db_table}' no está registrada en config.yaml (section: tables)."
