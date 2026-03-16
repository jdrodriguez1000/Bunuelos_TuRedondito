import os
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import hashlib
import json
import logging
import yaml
import subprocess
import time
from functools import wraps
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from src.connector.db_connector import DBConnector
from src.validator import DataValidator

# Configuración de logging profesional
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def backoff_retry(retries=3, backoff_factor=2):
    """Decorador para reintentar funciones con backoff exponencial [RSK-22]."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for i in range(retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    # Evitar reintentar si es un error de lógica de negocio o archivo no encontrado
                    if isinstance(e, (FileNotFoundError, KeyError)):
                        raise e
                    
                    wait = backoff_factor ** (i + 1)
                    if i < retries - 1:
                        logger.warning(f"⚠️ Reintentando {func.__name__} en {wait:.1f}s por error: {str(e)} ({i+1}/{retries})")
                        time.sleep(wait)
            raise last_exception
        return wrapper
    return decorator

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
        
        # Inicializar Validador de Contratos para Gatekeeper [BR-22-01]
        self.validator = DataValidator(self.config.get('validation', {}))

    def run_full_ingestion(self, execution_id: Optional[str] = None):
        """Orquesta la ingestión filtrando solo por tablas autorizadas en el contrato."""
        logger.info("🚀 Iniciando Proceso de Ingestión Unificada (Gobernada por Contrato)...")
        
        # 1. Cargar Contrato de Datos para verificar autorizaciones
        try:
            contract_path = self.config['contract']['path']
            with open(contract_path, 'r', encoding='utf-8') as f:
                contract = yaml.safe_load(f)
            
            # Crear mapa de autorizaciones basado en el nombre de la fuente del contrato
            # NOTA: En el contrato se llaman 'inventory', 'sales', etc. Que coinciden con los keys de config.ingestion.tables
            authorized_sources = {
                src['name']: src.get('enabled', False) 
                for src in contract.get('data_sources', [])
            }
        except Exception as e:
            logger.error(f"Error crítico cargando contrato en ingestor: {str(e)}")
            return {"failed": 1, "processed": 0, "details": [], "error": str(e)}

        # Usar ID externo si se provee
        if not execution_id:
            execution_id = str(hashlib.md5(datetime.now().isoformat().encode()).hexdigest())[:12]
        
        self.current_execution_id = execution_id
        summary = {"processed": 0, "failed": 0, "details": []}

        # 1.5 Gatekeeper de Gobernanza [BR-22-01]
        is_bootstrap = False
        failed_tables = []
        try:
            val_res = self.service_client.table("sys_validation_contract")\
                .select("status, support_json")\
                .order("created_at", desc=True)\
                .limit(1).execute()
            
            if not val_res.data:
                is_bootstrap = True
                logger.info("🚩 HITO 0 DETECTADO: No hay registros de gobernanza. Iniciando en Modo Bootstrap.")
            else:
                last_val = val_res.data[0]
                if last_val['status'] != 'VALID':
                    logger.warning("⛔ GATEKEEPER GLOBAL: La última validación de contrato falló. Abortando ingesta.")
                    return {"failed": 0, "processed": 0, "details": [], "status": "BLOCKED_BY_GATEKEEPER"}
                
                # Extraer metadatos de la última corrida
                support = last_val.get('support_json', {})
                tables_meta = support.get('tables', {}) # Diccionario de resultados previos
                
                # Identificar tablas que fallaron explícitamente (No certificadas)
                # Las tablas que NO están en tables_meta se consideran NUEVAS y se permiten.
                failed_tables = [
                    t_meta['db_table'] for t_meta in tables_meta.values()
                    if t_meta.get('certification_status') != 'CERTIFIED'
                ]
        except Exception as e:
            is_bootstrap = True # Fallback seguro: si falla la consulta, tratar como bootstrap pero validar
            logger.warning(f"⚠️ Error verificando Gatekeeper: {str(e)}. Por seguridad se activa Modo Bootstrap.")

        # 2. Filtrar fuentes: Solo las configuradas Y habilitadas Y certificadas (Gatekeeper)
        authorized_sources = []
        for src in contract.get('data_sources', []):
            if src.get('enabled'):
                r_name = src['db_table']
                # Verificación del Gatekeeper:
                # 1. Si la tabla falló en la última corrida, se bloquea (failed_tables).
                # 2. Si es nueva o pasó, se autoriza.
                if r_name not in failed_tables:
                    authorized_sources.append(src)
                else:
                    logger.warning(f"⛔ GATEKEEPER: Tabla '{r_name}' sigue bloqueada por fallo en certificación previa.")
        
        logger.info(f"Fuentes autorizadas por contrato y gatekeeper: {[s['name'] for s in authorized_sources]}")

        for source in authorized_sources:
                
            table_id_contract = source['name']
            real_table_name = source['db_table']
            
            # Buscar settings en la configuración de la ingesta (puede ser por ID o por nombre de tabla)
            settings = self.ingestion_config.get(table_id_contract, self.ingestion_config.get(real_table_name, {}))
            
            try:
                logger.info(f"--- Procesando Tabla: {real_table_name} (Origen: {table_id_contract}) ---")
                try:
                    logger.info(f"🚀 Iniciando Auditoría para {real_table_name}...")
                    strategy = "FULL" # Default strategy
                    last_audit = self._get_last_audit_state(real_table_name)
                    current_count = self._get_remote_count(real_table_name)
                except Exception as e:
                    logger.error(f"🚨 Error al obtener estado de auditoría o conteo remoto para {real_table_name}: {str(e)}")
                    self._log_audit(execution_id, real_table_name, "FAILED", 0.0, 0, {"error": f"Error inicial: {str(e)}"}, load_type="UNKNOWN")
                    summary["failed"] += 1
                    continue
                
                # 3. Validación de Contrato Estricta (Especial Hito 0 / Primeras Cargas)
                # Si no hay auditoría previa o estamos en bootstrap, validamos contrato antes de seguir
                if is_bootstrap or not last_audit:
                    logger.info(f"🔍 Validación de Contrato de Emergencia (Hito 0) para: {real_table_name}")
                    # Descargamos una muestra para validar estructura
                    sample_df = self._fetch_all_data(real_table_name, batch_size=50) 
                    
                    if not sample_df.empty:
                        # Extraer el trozo del contrato para esta tabla
                        table_contract = next((s for s in contract.get('data_sources', []) if s['db_table'] == real_table_name), None)
                        if table_contract:
                            val_report = self.validator.validate_table(real_table_name, sample_df, table_contract)
                            if val_report['status'] != 'VALID':
                                logger.error(f"❌ FALLO DE CONTRATO EN HITO 0: {val_report['errors']}")
                                self._log_audit(execution_id, real_table_name, "FAILED", 0.0, 0, {"error": "Fallo estructural en carga inicial", "details": val_report['errors']}, load_type=strategy)
                                summary["failed"] += 1
                                continue
                            logger.info(f"✅ Estructura validada exitosamente para {real_table_name}.")
                        else:
                            logger.warning(f"⚠️ No se encontró definición de contrato para {real_table_name}. Se procede bajo riesgo.")
                
                strategy = "FULL"
                last_row_count = last_audit.get('row_count', 0) if last_audit else 0
                
                # 2. Check for Incremental Load Possibility
                if last_audit and current_count == last_row_count:
                    strategy = "SKIP"
                    logger.info(f"   ✅ Sin cambios detectados (Puntero: {current_count} filas). Saltando descarga.")
                elif last_audit and current_count > last_row_count:
                    strategy = "INCREMENTAL"
                    logger.info(f"   📈 Detectadas {current_count - last_row_count} nuevas filas. Iniciando descarga incremental.")
                else: # last_audit is None or current_count < last_row_count (data loss or first load)
                    strategy = "FULL"
                    logger.info(f"   🔄 Carga Completa requerida (Refresh o Primera Carga).")

                # 3. Descarga Inteligente (Incremental vs Full)
                if strategy == "SKIP":
                    score_to_reuse = last_audit.get('health_score', 100.0)
                    h_report_to_reuse = last_audit.get('health_report', {})
                    s_hash_to_reuse = last_audit.get('semantic_hash')
                    
                    # Registrar auditoría de re-uso para trazabilidad en esta ejecución
                    self._log_audit(execution_id, real_table_name, "SUCCESS", score_to_reuse, current_count, h_report_to_reuse, s_hash_to_reuse, load_type="SKIP")

                    summary["details"].append({
                        "table": real_table_name,
                        "status": "NO_NEW_DATA",
                        "strategy": strategy,
                        "row_count": current_count,
                        "score": score_to_reuse,
                        "health_check": h_report_to_reuse,
                        "semantic_hash": s_hash_to_reuse
                    })
                    summary["processed"] += 1
                    continue

                # Carga de data base (si es incremental/refresh)
                df_base = pd.DataFrame()
                start_row = 0
                
                if strategy == "INCREMENTAL":
                    # Intentar cargar lo que ya tenemos en Bronce para completar el DF
                    # Si no hay archivo local, bajamos todo (Refresh forzado)
                    local_files = [f for f in os.listdir(self.bronze_path) if f.startswith(f"{real_table_name}_")]
                    if local_files:
                        # Cargar el más reciente
                        local_files.sort(reverse=True)
                        try:
                            df_base = pd.read_parquet(os.path.join(self.bronze_path, local_files[0]))
                            start_row = len(df_base)
                            logger.info(f"   📂 Base local cargada: {len(df_base)} filas. Descargando delta desde fila {start_row}...")
                        except:
                            logger.warning("   ⚠️ No se pudo leer base local. Iniciando descarga completa.")
                            strategy = "FULL"
                            start_row = 0
                    else:
                        strategy = "FULL"
                        start_row = 0

                # Descarga de la porción necesaria
                df_delta = self._fetch_all_data(real_table_name, start_row=start_row)
                
                # Combinar
                df = pd.concat([df_base, df_delta], ignore_index=True) if not df_base.empty else df_delta
                
                if df.empty:
                    error_msg = f"La tabla {real_table_name} está vacía en Supabase."
                    logger.warning(f"⚠️ {error_msg}")
                    
                    # Log NO_DATA en auditoría (SPEC-F02-02)
                    self._log_audit(execution_id, real_table_name, "NO_DATA", 0, 0, {"error": error_msg}, load_type=strategy)

                    summary["details"].append({
                        "table": real_table_name,
                        "status": "NO_DATA",
                        "error": error_msg,
                        "df": pd.DataFrame(),
                        "health_check": {"quality_metrics": {"null_columns": []}, "error": error_msg},
                        "row_count": 0
                    })
                    summary["processed"] += 1
                    continue

                # 3. Auditoría de Salud y Validación (Integrando muestras Head/Tail/Random)
                health_report, health_score = self._run_health_audit(df, table_id_contract, settings)
                
                # 4. Generación de Hash Semántico e Inmutabilidad
                semantic_hash = self._generate_file_hash(df, real_table_name)
                
                # 5. Guardado en Bronce (Parquet)
                file_name = f"{real_table_name}_{semantic_hash[:8]}.parquet"
                full_path = os.path.normpath(os.path.join(self.bronze_path, file_name))
                
                table = pa.Table.from_pandas(df)
                pq.write_table(table, full_path, compression='snappy')
                logger.info(f"✅ Archivo persistido: {file_name}")

                # 6. Sincronización Remota Obligatoria (DVC Push) [REQ-22-04]
                cloud_sync = self._sync_to_cloud(full_path)
                
                if not cloud_sync:
                    logger.warning(f"⚠️ Falló sincronización remota de {real_table_name}. El archivo queda solo local.")

                # 7. Mapeo de Estatus para Registro Oficial (SPEC-F02-02)
                # SUCCESS, FAILED, NO_DATA
                if not cloud_sync:
                    db_status = "FAILED"
                    internal_status = "S3_SYNC_FAILED"
                elif health_score < 60:
                    db_status = "FAILED"
                    internal_status = "WARNING"
                else:
                    db_status = "SUCCESS"
                    internal_status = "SUCCESS"

                self._log_audit(execution_id, real_table_name, db_status, health_score, len(df), health_report, semantic_hash, load_type=strategy)
                 
                summary["processed"] += 1
                summary["details"].append({
                    "table": real_table_name, 
                    "status": internal_status, 
                    "strategy": strategy,
                    "score": health_score,
                    "row_count": len(df),
                    "health_check": health_report,
                    "semantic_hash": semantic_hash,
                    "df": df 
                })

            except Exception as e:
                logger.error(f"🚨 Error fatal procesando {real_table_name}: {str(e)}")
                summary["failed"] += 1
                summary["details"].append({
                    "table": real_table_name,
                    "status": "NO_DATA",
                    "error": str(e),
                    "df": pd.DataFrame(),
                    "health_check": {"quality_metrics": {"null_columns": []}, "error": str(e)},
                    "row_count": 0
                })
                try:
                    self._log_audit(execution_id, real_table_name, "FAILED", 0, 0, {"error": str(e)}, load_type=strategy)
                except: pass

        logger.info(f"🏁 Ingestión Finalizada. Procesadas: {summary['processed']}, Fallidas: {summary['failed']}")
        return summary

    @backoff_retry(retries=3)
    def _get_remote_count(self, table_name: str) -> int:
        """Obtiene el conteo exacto de filas en el origen remoto."""
        try:
            res = self.service_client.table(table_name).select("*", count='exact').limit(1).execute()
            return res.count if res.count is not None else 0
        except Exception as e:
            logger.warning(f"⚠️ Error en conteo remoto ({table_name}): {str(e)}")
            raise e # Lanzar para que el decorador actúe

    @backoff_retry(retries=2)
    def _get_last_audit_state(self, table_name: str) -> Optional[Dict]:
        """Consulta el último estado de auditoría exitoso para una tabla."""
        try:
            res = self.service_client.table(self.config['tables']['sys_ingestion_audit'])\
                .select("row_count, semantic_hash, health_report, health_score")\
                .eq("table_name", table_name)\
                .eq("status", "SUCCESS")\
                .order("created_at", desc=True)\
                .limit(1).execute()
            return res.data[0] if res.data else None
        except Exception as e:
            logger.warning(f"⚠️ Error consultando estado previo ({table_name}): {str(e)}")
            raise e

    @backoff_retry(retries=3)
    def _fetch_all_data(self, table_name: str, batch_size: int = 1000, start_row: int = 0) -> pd.DataFrame:
        """
        Descarga registros de una tabla usando paginación de Supabase.
        Soporta descarga incremental mediante 'start_row'.
        """
        all_data = []
        start = start_row
        
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

    def _sync_to_cloud(self, file_path: str) -> bool:
        """
        Sincroniza el archivo con storage remoto vía DVC y verifica existencia [OPS-4.1].
        """
        try:
            file_name = os.path.basename(file_path)
            logger.info(f"   ☁️ Sincronizando con nube (DVC): {file_name}")
            
            # 1. dvc add
            result_add = subprocess.run(["dvc", "add", file_path], capture_output=True, text=True)
            if result_add.returncode != 0:
                logger.error(f"   ❌ Falló 'dvc add': {result_add.stderr}")
                return False
            logger.info(f"   [DVC] Archivo añadido localmente ({file_name})")
            
            # 2. dvc push (Sincroniza con S3 usando el remoto configurado)
            result_push = subprocess.run(["dvc", "push", "-r", "storage"], capture_output=True, text=True)
            if result_push.returncode != 0:
                logger.error(f"   ❌ Falló 'dvc push': {result_push.stderr}")
                return False
            
            # 3. Verificación Real de Existencia en el Remoto (SPEC-F02-02)
            check_cmd = ["dvc", "status", "-r", "storage", file_path]
            check_res = subprocess.run(check_cmd, capture_output=True, text=True)
            
            # Si no hay salida o si la salida dice que está sincronizado, es un éxito
            stdout = check_res.stdout.strip()
            if not stdout or "in sync" in stdout.lower():
                logger.info(f"   ✅ Verificación remota exitosa: {file_name} confirmado en storage.")
                return True
            else:
                logger.error(f"   ❌ Fallo de verificación remota. El archivo no parece estar sincronizado.")
                logger.error(f"   DEBUG DVC STATUS: {check_res.stdout}")
                return False
                
        except Exception as e:
            logger.error(f"   ❌ Error en DVC Sync/Verify: {str(e)}")
            return False

    def _run_health_audit(self, df: pd.DataFrame, table_id: str, settings: Dict) -> Tuple[Dict, float]:
        """
        Calcula indicadores de salud, gaps y reglas de negocio.
        """
        report = {
            "samples": {
                "head": df.head(3).to_dict(orient='records') if not df.empty else [],
                "tail": df.tail(3).to_dict(orient='records') if not df.empty else [],
                "random": df.sample(min(3, len(df))).to_dict(orient='records') if not df.empty else []
            },
            "quality_metrics": {
                "null_columns": [col for col in df.columns if df[col].isna().any()] if not df.empty else [],
                "duplicate_rows": int(df.duplicated().sum()) if not df.empty else 0,
                "sentinel_values_found": self._check_sentinels(df, settings.get('sentinels', [])),
                "custom_rules_violations_raw": self._check_custom_rules_v2(df, settings.get('custom_rules', []))
            },
            "time_analysis": {
                "frequency": settings.get('frequency', 'D'),
                **self._analyze_time_series(df, settings.get('frequency', 'D'))
            }
        }
        
        # Extraer métricas de tiempo para reporte de calidad
        report["quality_metrics"]["invalid_dates"] = report["time_analysis"].get("invalid_dates_count", 0)
        report["quality_metrics"]["null_pct"] = self._calculate_null_pct(df)
        
        # Inyectar lista de mensajes legibles para compatibilidad con el dashboard
        report["quality_metrics"]["custom_rules_violations"] = [v['message'] for v in report["quality_metrics"]["custom_rules_violations_raw"]]

        # CÁLCULO DE HEALTH SCORE PONDERADO (Weighted Aggregate Score) [RSK-22]
        scoring_conf = self.config.get('ingestion', {}).get('scoring', {})
        weights = scoring_conf.get('weights', {})
        penalties = scoring_conf.get('penalties', {})

        # Pilar 1: Reglas de Negocio (Business Rules) - 50%
        # Penalización mucho más agresiva: 
        # 1. Penalización fija por cualquier falla (Asegura que el score baje de 100 de inmediato)
        # 2. Penalización proporcional al % de registros que fallan
        violations_data = report["quality_metrics"]["custom_rules_violations_raw"]
        business_score = 100.0
        
        if violations_data:
            total_fails = sum(v['fails'] for v in violations_data)
            fail_pct = (total_fails / len(df)) * 100 if not df.empty else 0
            
            # Penalización fija: 15 puntos por el simple hecho de tener violaciones de negocio
            fixed_penalty = 15.0
            
            # Penalización variable: % de fallos * factor (ej. 2.0)
            variable_penalty = fail_pct * penalties.get('per_custom_rule_violation_pct', 2.0)
            
            # Penalización por regla distinta que falla: 5 puntos por cada regla única fallida
            rule_count_penalty = len(violations_data) * 5.0
            
            business_score = 100.0 - fixed_penalty - variable_penalty - rule_count_penalty
        
        # Pilar 2: Continuidad Temporal (Time Continuity) - 20%
        # Penalización por cada día de Gap
        gaps_count = len(report["time_analysis"]["gaps_detected"])
        continuity_score = 100.0 - (gaps_count * penalties.get('per_gap_day', 5))
        if report["time_analysis"]["freshness_lag_days"] > 7: continuity_score -= 10
        if report["time_analysis"]["has_leakage"]: continuity_score = 0 # Data del futuro es inaceptable

        # Pilar 3: Integridad Técnica (Data Integrity) - 20%
        # Basado en Nulos y Fechas Inválidas
        null_penalty = max(0, report["quality_metrics"]["null_pct"] - penalties.get('max_null_pct_allowed', 1.0)) * 5
        invalid_date_penalty = report["quality_metrics"]["invalid_dates"] * penalties.get('per_invalid_date', 10)
        integrity_score = 100.0 - null_penalty - invalid_date_penalty

        # Pilar 4: Higiene / Limpieza (Data Cleaning) - 10%
        cleaning_score = 100.0
        if report["quality_metrics"]["duplicate_rows"] > 0: cleaning_score -= 15
        if report["quality_metrics"]["sentinel_values_found"]: cleaning_score -= 10

        # Ensamble Ponderado Final
        final_score = (
            (max(0, business_score) * weights.get('business_rules', 0.50)) +
            (max(0, continuity_score) * weights.get('time_continuity', 0.20)) +
            (max(0, integrity_score) * weights.get('data_integrity', 0.20)) +
            (max(0, cleaning_score) * weights.get('data_cleaning', 0.10))
        )

        # Inyectar sub-scores en el reporte para el Dashboard (Visualización de pilares)
        report["health_dimensions"] = {
            "business": round(business_score, 2),
            "continuity": round(continuity_score, 2),
            "integrity": round(integrity_score, 2),
            "cleaning": round(cleaning_score, 2)
        }

        return report, round(max(0.0, final_score), 1)

    def _calculate_null_pct(self, df: pd.DataFrame) -> float:
        """Calcula el porcentaje global de valores nulos."""
        if df.empty: return 0.0
        return round((df.isna().sum().sum() / (df.shape[0] * df.shape[1])) * 100, 2)

    def _check_sentinels(self, df: pd.DataFrame, sentinels: List) -> Dict[str, int]:
        """Cuenta apariciones de valores centinela por columna."""
        hits = {}
        for col in df.columns:
            # Manejar comparaciones con tipos mixtos (strings y números)
            count = df[col].isin(sentinels).sum()
            if count > 0:
                hits[col] = int(count)
        return hits

    def _check_custom_rules_v2(self, df: pd.DataFrame, rules: List[Dict]) -> List[Dict]:
        """
        Versión mejorada que extrae conteos precisos de fallos para scoring agresivo.
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
                    fail_count = int(failed_mask.sum())
                    if fail_count > 0:
                        violations.append({
                            "rule": name,
                            "fails": fail_count,
                            "message": f"{name}: {fail_count} registros tienen valores negativos en campos numéricos."
                        })
                    continue

                # 2. Transformación de Operador de Implicación: A => B  es  (not A) or B
                processed_expr = expr
                if "=>" in expr:
                    antecedent, consequent = expr.split("=>")
                    processed_expr = f"(~({antecedent.strip()})) | ({consequent.strip()})"

                # 3. Evaluación segura con Pandas
                mask = df.eval(processed_expr, engine='python')
                
                # Para implicaciones o booleanos, la máscara indica CUMPLIMIENTO (True)
                fail_count = int((~mask).sum())
                
                if fail_count > 0:
                    violations.append({
                        "rule": name,
                        "fails": fail_count,
                        "message": f"{name}: {fail_count} registros fallaron la validación."
                    })
                    
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
        # Coerción estricta de fechas [RSK-22]
        temp_dates = pd.to_datetime(df[col], errors='coerce')
        invalid_count = int(temp_dates.isna().sum())
        analysis["invalid_dates_count"] = invalid_count
        
        # Filtrar solo fechas válidas para el análisis de gaps y freshness
        valid_dates = temp_dates.dropna().sort_values().unique()
        
        if len(valid_dates) < 2:
            return analysis

        # 1. Freshness y Leakage (Point-in-Time Check Profesional)
        # 1. Freshness y Leakage (Point-in-Time Check Profesional consciente de Frecuencia)
        last_date = pd.Timestamp(valid_dates[-1])
        now = pd.Timestamp.now().normalize()
        
        # Lógica de Frescura con Ventana de Transición (Hito 0/M/Y support)
        if frequency == 'M':
            is_current_month = (last_date.year == now.year and last_date.month == now.month)
            is_transition_day = (now.day == 1)
            prev_month = now - pd.DateOffset(months=1)
            is_last_month = (last_date.year == prev_month.year and last_date.month == prev_month.month)
            
            # Durante el mes, o el día 1 con data del mes anterior, el lag es 0
            analysis["freshness_lag_days"] = 0 if (is_current_month or (is_transition_day and is_last_month)) else (now - last_date).days
        elif frequency == 'Y':
            is_current_year = (last_date.year == now.year)
            is_transition_day = (now.day == 1 and now.month == 1)
            is_last_year = (last_date.year == now.year - 1)
            
            analysis["freshness_lag_days"] = 0 if (is_current_year or (is_transition_day and is_last_year)) else (now - last_date).days
        else:
            analysis["freshness_lag_days"] = (now - last_date).days

        # Leakage: Si la data es del futuro respecto al momento de ingesta
        analysis["has_leakage"] = last_date > now

        # 2. Gaps Multidimensionales (D, W, M, Y)
        try:
            # Solo detectamos Gaps si tenemos al menos 2 fechas
            if len(valid_dates) > 1:
                # Generar rango teórico basado en la frecuencia configurada
                start_date = pd.Timestamp(valid_dates[0])
                end_date = pd.Timestamp(valid_dates[-1])
                
                # Mapeo de frecuencias de config.yaml a pandas offset aliases
                freq_map = {'D': 'D', 'W': 'W', 'M': 'MS', 'Y': 'YS'}
                pd_freq = freq_map.get(frequency, 'D')
                
                full_range = pd.date_range(start=start_date, end=end_date, freq=pd_freq)
                missing = full_range.difference(valid_dates)
                
                if not missing.empty:
                    analysis["gaps_detected"] = [d.strftime('%Y-%m-%d') for d in missing[:15]] # Top 15
        except Exception as e:
            logger.warning(f"⚠️ Error calculando Gaps: {str(e)}")
            
        return analysis

    def _generate_file_hash(self, df: pd.DataFrame, table_name: str) -> str:
        """Huella digital inmutable para el archivo Parquet."""
        # Usar la estructura y una muestra para el hash
        sample = df.sample(min(10, len(df))).to_json()
        raw = f"{table_name}|{len(df)}|{sample}"
        return hashlib.sha256(raw.encode()).hexdigest()

    @backoff_retry(retries=3)
    def _log_audit(self, exec_id: str, table_name: str, status: str, score: float, count: int, report: Dict, s_hash: str = "N/A", load_type: str = "FULL"):
        """Inserta el registro de auditoría en la tabla sys_ingestion_audit [T-2.2-03]."""
        payload = {
            "execution_id": exec_id,
            "table_name": table_name,
            "semantic_hash": s_hash if s_hash != "N/A" else f"MISSING_{exec_id}",
            "status": status,
            "health_score": score,
            "row_count": count,
            "load_type": load_type,
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
