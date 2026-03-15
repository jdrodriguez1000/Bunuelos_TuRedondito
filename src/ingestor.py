import os
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from src.connector.db_connector import DBConnector
from src.validator import DataValidator

# Configuración de logging profesional
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UnifiedIngestor:
    """
    Motor de Ingestión Física y Auditoría de Salud (Stage 2.2).
    Implementa: Descarga por batches, Hashing Semántico, Validación de Reglas de Negocio
    y persistencia en Capa Bronce (Parquet).
    """

    def __init__(self):
        self.connector = DBConnector()
        self.config = self.connector.get_config()
        self.service_client = self.connector.get_service_client()
        self.bronze_path = self.config.get('bronze', {}).get('path', 'data/bronze')
        self.ingestion_config = self.config.get('ingestion', {}).get('tables', {})
        
        # Asegurar que el directorio de datos existe
        os.makedirs(self.bronze_path, exist_ok=True)

    def run_full_ingestion(self):
        """Orquesta la ingestión de todas las tablas configuradas."""
        logger.info("🚀 Iniciando Proceso de Ingestión Unificada...")
        execution_id = str(hashlib.md5(datetime.now().isoformat().encode()).hexdigest())[:12] # ID temporal
        
        summary = {"processed": 0, "failed": 0, "details": []}

        for table_id, settings in self.ingestion_config.items():
            try:
                # 1. Extraer nombre real de la tabla desde el mapeo global
                real_table_name = self.config.get('tables', {}).get(table_id)
                if not real_table_name:
                    logger.error(f"❌ No se encontró mapeo real para {table_id}")
                    continue

                logger.info(f"--- Procesando Tabla: {real_table_name} ---")
                
                # 2. Descarga por batches (Supabase Pagination)
                df = self._fetch_all_data(real_table_name)
                
                if df.empty:
                    self._log_audit(execution_id, real_table_name, "NO_DATA", 0, 0, {})
                    summary["processed"] += 1
                    continue

                # 3. Auditoría de Salud y Validación
                health_report, health_score = self._run_health_audit(df, table_id, settings)
                
                # 4. Generación de Hash Semántico e Inmutabilidad
                semantic_hash = self._generate_file_hash(df, real_table_name)
                
                # 5. Guardado en Bronce (Parquet)
                file_name = f"{real_table_name}_{semantic_hash[:8]}.parquet"
                full_path = os.path.join(self.bronze_path, file_name)
                
                table = pa.Table.from_pandas(df)
                pq.write_table(table, full_path, compression='snappy')
                logger.info(f"✅ Archivo persistido: {file_name}")

                # 6. Registro oficial en Supabase Audit
                status = "SUCCESS" if health_score >= 80 else "WARNING"
                self._log_audit(execution_id, real_table_name, status, health_score, len(df), health_report, semantic_hash)
                
                summary["processed"] += 1
                summary["details"].append({"table": real_table_name, "status": status, "score": health_score})

            except Exception as e:
                logger.error(f"🚨 Error fatal procesando {table_id}: {str(e)}")
                summary["failed"] += 1
                # En caso de error, intentar loggear el fallo si es posible
                try:
                    self._log_audit(execution_id, table_id, "FAILED", 0, 0, {"error": str(e)})
                except: pass

        logger.info(f"🏁 Ingestión Finalizada. Procesadas: {summary['processed']}, Fallidas: {summary['failed']}")
        return summary

    def _fetch_all_data(self, table_name: str, batch_size: int = 1000) -> pd.DataFrame:
        """
        Descarga todos los registros de una tabla usando paginación de Supabase.
        Supera el límite de 1000 registros del API.
        """
        all_data = []
        start = 0
        
        while True:
            # Solicitar rango de datos (Supabase pagination)
            response = self.service_client.table(table_name).select("*").range(start, start + batch_size - 1).execute()
            data = response.data
            
            if not data:
                break
            
            all_data.extend(data)
            
            if len(data) < batch_size:
                break
                
            start += batch_size
            logger.info(f"   📥 Descargando... {len(all_data)} registros obtenidos.")

        return pd.DataFrame(all_data)

    def _run_health_audit(self, df: pd.DataFrame, table_id: str, settings: Dict) -> Tuple[Dict, float]:
        """
        Calcula indicadores de salud, gaps y reglas de negocio.
        """
        report = {
            "samples": {
                "head": df.head(3).to_dict(orient='records'),
                "tail": df.tail(3).to_dict(orient='records'),
                "random": df.sample(min(3, len(df))).to_dict(orient='records')
            },
            "quality_metrics": {
                "null_pct": (df.isna().sum().sum() / df.size) * 100 if not df.empty else 0,
                "sentinel_hits": self._check_sentinels(df, settings.get('sentinels', [])),
                "custom_rules_violations": self._check_custom_rules(df, settings.get('custom_rules', []))
            },
            "time_analysis": self._analyze_time_series(df, settings.get('frequency', 'D'))
        }

        # Cálculo de Health Score Simplificado (0-100)
        # Penalizaciones: 
        # - 20% si hay nulos significativos
        # - 30% si hay violaciones de reglas de negocio
        # - 10% por centinelas encontrados
        # - 40% si hay Gaps en el tiempo
        score = 100.0
        if report["quality_metrics"]["null_pct"] > 5: score -= 10
        if report["quality_metrics"]["sentinel_hits"]: score -= 20
        if report["quality_metrics"]["custom_rules_violations"]: score -= 30
        if report["time_analysis"]["gaps_detected"]: score -= 40

        return report, max(0.0, score)

    def _check_sentinels(self, df: pd.DataFrame, sentinels: List) -> Dict[str, int]:
        """Cuenta apariciones de valores centinela por columna."""
        hits = {}
        for col in df.columns:
            # Manejar comparaciones con tipos mixtos (strings y números)
            count = df[col].isin(sentinels).sum()
            if count > 0:
                hits[col] = int(count)
        return hits

    def _check_custom_rules(self, df: pd.DataFrame, rules: List[Dict]) -> List[str]:
        """
        Valida reglas de negocio dinámicas definidas en config.yaml.
        Soporta: Macros (all_fields), Implicación (=>), Operaciones Matemáticas.
        """
        violations = []
        if df.empty:
            return violations

        for rule in rules:
            name = rule.get('name')
            expr = rule.get('expression')
            
            try:
                # 1. Macro: all_fields >= 0
                if "all_fields >= 0" in expr:
                    numeric_df = df.select_dtypes(include=['number'])
                    failed_mask = (numeric_df < 0).any(axis=1)
                    fail_count = failed_mask.sum()
                    if fail_count > 0:
                        violations.append(f"{name}: {fail_count} registros tienen valores negativos en campos numéricos.")
                    continue

                # 2. Transformación de Operador de Implicación: A => B  es  (not A) or B
                if "=>" in expr:
                    antecedent, consequent = expr.split("=>")
                    # En pandas eval: (~(antecedente)) | (consecuente)
                    expr = f"(~({antecedent.strip()})) | ({consequent.strip()})"

                # 3. Evaluación segura con Pandas
                # Nota: engine='python' permite más flexibilidad en expresiones complejas
                mask = df.eval(expr, engine='python')
                
                # Para implicaciones o booleanos, la máscara indica CUMPLIMIENTO (True)
                fail_count = (~mask).sum()
                
                if fail_count > 0:
                    violations.append(f"{name}: {fail_count} registros fallaron la validación.")
                    
            except Exception as e:
                logger.warning(f"⚠️ Salto de regla '{name}' por error técnico: {str(e)}")
        
        return violations

    def _analyze_time_series(self, df: pd.DataFrame, frequency: str) -> Dict:
        """Detecta Gaps, Freshness y Leakage si hay columna de fecha."""
        date_cols = [c for c in df.columns if 'fecha' in c or 'date' in c or 'timestamp' in c]
        analysis = {"gaps_detected": [], "freshness_lag_days": 0, "has_leakage": False}
        
        if not date_cols:
            return analysis
            
        col = date_cols[0]
        dates = pd.to_datetime(df[col]).sort_values().unique()
        
        if len(dates) < 2:
            return analysis

        # 1. Freshness y Leakage
        last_date = pd.Timestamp(dates[-1])
        today = pd.Timestamp.now().normalize()
        analysis["freshness_lag_days"] = (today - last_date).days
        analysis["has_leakage"] = last_date > today

        # 2. Gaps (Solo para frecuencia diaria "D")
        if frequency == 'D':
            full_range = pd.date_range(start=dates[0], end=dates[-1], freq='D')
            missing = full_range.difference(dates)
            analysis["gaps_detected"] = [d.strftime('%Y-%m-%d') for d in missing[:10]] # Top 10
            
        return analysis

    def _generate_file_hash(self, df: pd.DataFrame, table_name: str) -> str:
        """Huella digital inmutable para el archivo Parquet."""
        # Usar la estructura y una muestra para el hash
        sample = df.sample(min(10, len(df))).to_json()
        raw = f"{table_name}|{len(df)}|{sample}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def _log_audit(self, exec_id: str, table_name: str, status: str, score: float, count: int, report: Dict, s_hash: str = "N/A"):
        """Inserta el registro de auditoría en la tabla sys_ingestion_audit [T-2.2-03]."""
        payload = {
            "execution_id": exec_id,
            "table_name": table_name,
            "semantic_hash": s_hash if s_hash != "N/A" else f"MISSING_{exec_id}",
            "status": status,
            "health_score": score,
            "row_count": count,
            "health_report": report
        }
        
        try:
            self.service_client.table("sys_ingestion_audit").insert(payload).execute()
            logger.info(f"📝 Auditoría registrada para {table_name} (Score: {score})")
        except Exception as e:
            logger.error(f"❌ Falló registro de auditoría en Supabase: {str(e)}")

if __name__ == "__main__":
    # Test rápido de ejecución
    ingestor = UnifiedIngestor()
    ingestor.run_full_ingestion()
