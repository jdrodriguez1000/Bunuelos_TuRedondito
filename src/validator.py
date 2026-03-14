import pandas as pd
import hashlib
import json
import logging
from datetime import datetime
from typing import Dict, Any, Tuple, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ContractViolationError(Exception):
    """Excepción personalizada para fallos críticos en el contrato de datos."""
    pass

class DataValidator:
    """
    Motor de Validación Agnóstico (Etapa 2.1).
    Valida integridad estructural, descriptiva y genera huella digital semántica.
    """

    def __init__(self, validation_config: Dict[str, Any]):
        self.config = validation_config
        self.thresholds = self.config.get('thresholds', {})
        self.fingerprint_alg = self.config.get('fingerprint', {}).get('algorithm', 'sha256')

    def validate_table(self, table_name: str, df: pd.DataFrame, table_contract: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta el pipeline de validación para una tabla específica.
        """
        logger.info(f"Iniciando validación para tabla: {table_name}")
        
        report = {
            "table": table_name,
            "timestamp": datetime.now().isoformat(),
            "status": "VALID",
            "row_count": len(df),
            "errors": [],
            "columns": {}
        }

        try:
            # 1. Validación Estructural (Nombres)
            self._check_columns_presence(df, table_contract, report)
            
            # 2. Validación de Tipos y Perfilamiento
            if report["status"] == "VALID":
                self._profile_and_validate_types(df, table_contract, report)
            
            # 3. Generación de Hash Semántico
            if report["status"] == "VALID":
                report["semantic_hash"] = self._generate_semantic_hash(df, table_contract)
            else:
                report["semantic_hash"] = "N/A"

        except Exception as e:
            logger.error(f"Error crítico validando {table_name}: {str(e)}")
            report["status"] = "INVALID"
            report["errors"].append(f"System Error: {str(e)}")

        return report

    def _check_columns_presence(self, df: pd.DataFrame, table_contract: Dict[str, Any], report: Dict[str, Any]):
        """Verifica que todas las columnas obligatorias existan."""
        contract_cols = set(table_contract.get('columns', {}).keys())
        df_cols = set(df.columns)
        
        missing = contract_cols - df_cols
        if missing:
            report["status"] = "INVALID"
            error_msg = f"Columnas faltantes en origen: {list(missing)}"
            report["errors"].append(error_msg)
            logger.warning(error_msg)

    def _profile_and_validate_types(self, df: pd.DataFrame, table_contract: Dict[str, Any], report: Dict[str, Any]):
        """Valida tipos de datos y genera estadísticos descriptivos."""
        columns_config = table_contract.get('columns', {})
        
        for col, config in columns_config.items():
            expected_type = config.get('type')
            col_report = {"status": "VALID", "type": expected_type}
            
            # Lógica por tipo con soporte para sinónimos
            if expected_type == 'datetime':
                self._validate_datetime(df, col, report, col_report)
            elif expected_type in ['numeric', 'int', 'float', 'decimal']:
                self._validate_numeric(df, col, report, col_report)
            elif expected_type in ['categorical', 'string', 'text', 'boolean']:
                self._validate_categorical(df, col, col_report)
            
            report["columns"][col] = col_report

    def _validate_datetime(self, df: pd.DataFrame, col: str, report: Dict[str, Any], col_report: Dict[str, Any]):
        """Validación específica para fechas con umbral de fallo."""
        original_nulls = df[col].isna().sum()
        
        # Intento de conversión forzada
        converted_series = pd.to_datetime(df[col], errors='coerce')
        new_nulls = converted_series.isna().sum()
        
        # Check de umbral NaT (BR-21-06)
        nat_increase = new_nulls - original_nulls
        if len(df) > 0:
            increase_pct = nat_increase / len(df)
            max_allowed = self.thresholds.get('max_nat_increase_pct', 0.05)
            
            if increase_pct > max_allowed:
                report["status"] = "INVALID"
                col_report["status"] = "INVALID"
                report["errors"].append(f"Columna {col}: {increase_pct:.2%} de datos no son fechas válidas (Máx: {max_allowed:.2%})")

        col_report["stats"] = {
            "min": str(converted_series.min()) if not converted_series.empty else None,
            "max": str(converted_series.max()) if not converted_series.empty else None,
            "nat_increase": int(nat_increase)
        }

    def _validate_numeric(self, df: pd.DataFrame, col: str, report: Dict[str, Any], col_report: Dict[str, Any]):
        """Validación de numéricos y detección de outliers básicos."""
        series = pd.to_numeric(df[col], errors='coerce')
        
        # Estadísticos base
        mean = series.mean()
        std = series.std()
        
        # Outliers (IQM simple)
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        outliers_count = ((series < lower_bound) | (series > upper_bound)).sum()

        col_report["stats"] = {
            "mean": float(mean) if not pd.isna(mean) else 0,
            "std": float(std) if not pd.isna(std) else 0,
            "min": float(series.min()) if not pd.isna(series.min()) else 0,
            "max": float(series.max()) if not pd.isna(series.max()) else 0,
            "q1": float(q1) if not pd.isna(q1) else 0,
            "median": float(series.median()) if not pd.isna(series.median()) else 0,
            "q3": float(q3) if not pd.isna(q3) else 0
        }
        col_report["outliers"] = {
            "count": int(outliers_count),
            "lower_bound": float(lower_bound),
            "upper_bound": float(upper_bound)
        }

    def _validate_categorical(self, df: pd.DataFrame, col: str, col_report: Dict[str, Any]):
        """Perfilamiento completo de frecuencias para categóricos."""
        # Calculamos frecuencias relativas y absolutas
        val_counts = df[col].value_counts()
        val_pcts = df[col].value_counts(normalize=True)
        
        freqs = {}
        # Limitamos a los top 20 para no inflar el reporte si hay miles de categorías, 
        # pero informamos el total de únicos.
        unique_count = len(val_counts)
        top_values = val_counts.head(20)
        
        for val, count in top_values.items():
            freqs[str(val)] = {
                "count": int(count),
                "percentage": float(val_pcts[val])
            }
        
        col_report["summary"] = {
            "unique_values": unique_count,
            "top_frequencies": freqs
        }

    def _generate_semantic_hash(self, df: pd.DataFrame, table_contract: Dict[str, Any]) -> str:
        """
        Genera el Semantic Fingerprint (BR-21-05).
        Basado en esquema, conteo y una muestra de datos para integridad.
        """
        # 1. Metadatos de estructura
        schema_info = json.dumps(table_contract.get('columns', {}), sort_keys=True)
        
        # 2. Resumen de datos
        row_count = str(len(df))
        sample_sum = ""
        
        # Usamos una muestra determinista de las primeras 5 filas para el hash
        if not df.empty:
            sample_sum = df.head(5).to_json()

        combined = f"{schema_info}|{row_count}|{sample_sum}"
        
        if self.fingerprint_alg == 'sha256':
            return hashlib.sha256(combined.encode()).hexdigest()
        return hashlib.md5(combined.encode()).hexdigest()
