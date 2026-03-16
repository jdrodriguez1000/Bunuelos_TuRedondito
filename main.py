import os
import yaml
import json
import logging
import argparse
import hashlib
import pandas as pd
from datetime import datetime
from typing import Dict, Any

import uuid
from src.validator import DataValidator
from src.connector.db_connector import DBConnector
from src.connector.cloud_certification import CloudCertifier
from src.ingestor import UnifiedIngestor

# Configuración de Logging Profesional
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ORCHESTRATOR")

class Orchestrator:
    """
    Orquestador Principal del Sistema Bunuelos_TuRedondito (CLI).
    Encargado de coordinar las etapas de carga, entrenamiento y predicción.
    """

    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config = self._load_yaml(config_path)
        self.validator = DataValidator(self.config.get('validation', {}))
        self.db = DBConnector() # Inicializa Singleton Guard
        self.certifier = CloudCertifier()
        self.ingestor = UnifiedIngestor() # Ingestor Físico (Stage 2.2)
        self.mandatory_source = self.config['contract']['mandatory_source']
        
    def _load_yaml(self, path: str) -> Dict[str, Any]:
        """Carga archivos YAML de configuración."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Archivo no encontrado: {path}")
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def load_data(self):
        """
        COMANDO: load
        Ejecuta el proceso de obtención, validación y certificación de ingesta.
        """
        logger.info("--- [ETAPA 2.2] Iniciando Proceso de Carga y Validación REAL ---")
        
        # 0. Inicializar Trazabilidad Total (Master Session)
        execution_uuid = str(uuid.uuid4())
        logger.info(f"Master Execution ID: {execution_uuid}")
        
        load_report = {
            "execution_id": execution_uuid,
            "timestamp": datetime.now().isoformat(),
            "status": "RUNNING",
            "load_type": "ORCHESTRATION_IN_PROGRESS",
            "tables": {},
            "summary": {"total": 0, "valid": 0, "invalid": 0},
            "error_msg": None
        }
        
        # Registrar inicio en sys_pipeline_execution para trazabilidad inmediata
        try:
            self.db.get_service_client().table(self.config['tables']['sys_pipeline_execution']).insert({
                "id": execution_uuid,
                "process_name": "unified_load_pipeline",
                "execution_mode": "load",
                "status": "RUNNING"
            }).execute()
        except Exception as e:
            logger.warning(f"No se pudo crear registro inicial de ejecución: {str(e)}")

        data_contract = {}

        try:
            # 1. Ejecutar Ingestión Física y Auditoría de Salud (Stage 2.2)
            # Pasamos el execution_uuid para amarrar los registros de sys_ingestion_audit
            ingestion_summary = self.ingestor.run_full_ingestion(execution_id=execution_uuid)
            
            if ingestion_summary.get("status") == "BLOCKED_BY_GATEKEEPER":
                logger.error("❌ Proceso abortado por el Gatekeeper (Contrato técnico inválido).")
                load_report["status"] = "FAILED"
                load_report["error_msg"] = "Blocked by Governance Gatekeeper (sys_validation_contract status != VALID)"
                self._save_report(load_report)
                return

            if ingestion_summary["failed"] > 0:
                logger.warning(f"⚠️ La ingestión terminó con {ingestion_summary['failed']} tablas fallidas.")
            
            logger.info(f"DEBUG INGESTION: Status={ingestion_summary.get('status')}, Details Count={len(ingestion_summary.get('details', []))}")
            if len(ingestion_summary.get('details', [])) == 0:
                logger.error(f"DEBUG: El Ingestor no devolvió detalles. Error: {ingestion_summary.get('error')}")

            # 2. Carga y Auditoría de Gobernanza (Contrato)
            contract_path = self.config['contract']['path']
            try:
                data_contract = self._load_yaml(contract_path)
                load_report["governance_audit"] = {
                    "contract_version": data_contract.get('version', 'unknown'),
                    "authorized_sources": [s['name'] for s in data_contract.get('data_sources', []) if s.get('enabled')],
                    "ignored_sources": [s['name'] for s in data_contract.get('data_sources', []) if not s.get('enabled')]
                }
            except Exception as e:
                error_txt = f"ERROR DE GOBIERNO: Falló la carga del contrato. {str(e)}"
                logger.error(error_txt)
                load_report["status"] = "FAILED"
                load_report["error_msg"] = error_txt
                raise

            # 3. Certificación Técnica de Resultados
            for detail in ingestion_summary.get("details", []):
                try:
                    table_name = detail.get("table", "unknown")
                    strategy = detail.get("strategy", "UNKNOWN")
                    
                    # --- LÓGICA DE SALTO (SKIP) SI NO HAY DATOS NUEVOS ---
                    if detail.get("status") == "NO_NEW_DATA":
                        logger.info(f"   ⏩ {table_name}: Sin cambios detectados. Reusando auditoría previa.")
                        # Buscar metadatos en el contrato
                        source_meta = next((s for s in data_contract.get('data_sources', []) if s['db_table'] == table_name), None)
                        source_name = source_meta['name'] if source_meta else table_name
                        
                        table_entry = {
                            "source_name": source_name,
                            "db_table": table_name,
                            "certification_status": "CERTIFIED",
                            "status_reason": "No changes (Strategy: SKIP)",
                            "strategy": "SKIP",
                            "metrics": {
                                "row_count": detail.get("row_count", 0),
                                "semantic_hash": detail.get("semantic_hash", "N/A"),
                                "health_score": detail.get("score", 100.0), # Score honesto desde el ingestor/historial
                                "duplicates_found": detail.get("health_check", {}).get("quality_metrics", {}).get("duplicate_rows", 0)
                            },
                            "structural_validation": {"status": "VALID", "reused": True},
                            "deep_health_audit": detail.get("health_check", {}),
                            "data_preview": detail.get("preview", {})
                        }
                        load_report["tables"][source_name] = table_entry
                        load_report["summary"]["total"] += 1
                        load_report["summary"]["valid"] += 1
                        continue

                    df_real = detail.get("df", pd.DataFrame())
                    logger.info(f"Certificando resultados para: {table_name} (Strategy: {strategy})")
                    
                    # Buscar metadatos en el contrato
                    source_meta = next((s for s in data_contract.get('data_sources', []) if s['db_table'] == table_name), None)
                    if not source_meta:
                        logger.warning(f"Tabla '{table_name}' no encontrada en el contrato.")
                        continue

                    source_name = source_meta['name']
                    
                    # 3. Validación Estructural vs Contrato
                    # Si no hay datos, relajamos la validación estructural (no podemos validar lo que no vemos)
                    if detail.get("status") == "NO_DATA":
                        structural_report = {"status": "VALID", "note": "Tabla vacía en origen, validación estructural saltada."}
                        status_flag = detail.get("status") not in ["FAILED", "S3_SYNC_FAILED"]
                    else:
                        table_contract = {'columns': {col: {'type': t} for col, t in source_meta.get('schema', {}).items()}}
                        structural_report = self.validator.validate_table(table_name, df_real, table_contract)
                        
                        # Construcción de Reporte de Tabla
                        status_flag = structural_report.get("status") == "VALID" and detail.get("status") not in ["FAILED", "S3_SYNC_FAILED"]
                    
                    # Extraer métricas de salud con seguridad total
                    health_data = detail.get("health_check", {})
                    q_metrics = health_data.get("quality_metrics", {})

                    table_entry = {
                        "source_name": source_name,
                        "db_table": table_name,
                        "certification_status": "CERTIFIED" if status_flag else "REJECTED",
                        "status_reason": detail.get("error") or structural_report.get("error_msg") or ("S3 Sync Failed" if detail.get("status") == "S3_SYNC_FAILED" else "Certified"),
                        "strategy": strategy,
                        "metrics": {
                            "row_count": detail.get("row_count", 0),
                            "semantic_hash": detail.get("semantic_hash", "N/A"),
                            "health_score": detail.get("score", 100.0), # Usar el score calculado por el ingestor
                            "duplicates_found": health_data.get("quality_metrics", {}).get("duplicate_rows", 0)
                        },
                        "structural_validation": structural_report,
                        "deep_health_audit": health_data,
                        "data_preview": detail.get("preview", {})
                    }

                    load_report["tables"][source_name] = table_entry
                    load_report["summary"]["total"] += 1
                    
                    if table_entry["certification_status"] == "CERTIFIED":
                        load_report["summary"]["valid"] += 1
                    else:
                        load_report["summary"]["invalid"] += 1
                        load_report["status"] = "FAILED"
                except Exception as table_err:
                    logger.error(f"Error procesando certificación de {detail.get('table')}: {str(table_err)}")
                    load_report["status"] = "FAILED"
                    continue

            # 4. Verificación de Integridad de la Carga
            if self.mandatory_source not in load_report["tables"] and load_report["status"] != "FAILED":
                 logger.error(f"CRÍTICO: La fuente obligatoria '{self.mandatory_source}' no fue procesada.")
                 load_report["status"] = "FAILED"
                 load_report["error_msg"] = f"Missing mandatory source: {self.mandatory_source}"

            # 5. Cierre de Proceso
            if load_report["status"] == "RUNNING":
                load_report["status"] = "SUCCESS"
            
            if load_report["status"] == "SUCCESS":
                load_report["load_type"] = self._determine_load_type(load_report)
                logger.info(f"Carga exitosa. Tipo: {load_report['load_type']}")
            else:
                load_report["load_type"] = "INVALID_PROCESS"

        except Exception as e:
            if not load_report["error_msg"]:
                load_report["error_msg"] = str(e)
            load_report["status"] = "FAILED"
            logger.error(f"Falla en flujo de orquestación: {load_report['error_msg']}")

        # 6. Persistencia y Auditoría (SIEMPRE ejecutada incluso en fallos)
        self._save_report(load_report)
        
        try:
            self._certify_and_log(load_report, data_contract)
        except Exception as e:
            logger.error(f"Error persistiendo auditoría de falla: {str(e)}")
            load_report["status"] = "FAILED"

        if load_report["status"] == "FAILED":
            logger.error(f"❌ Carga FINALIZADA CON ERRORES.")
        else:
            logger.info(f"✅ Carga EXITOSA ({load_report['load_type']}).")

    def _fetch_from_supabase(self, table_name: str) -> pd.DataFrame:
        """Descarga datos reales desde Supabase usando el Service Role."""
        try:
            logger.info(f"Descargando datos de {table_name}...")
            client = self.db.get_service_client()
            response = client.table(table_name).select("*").execute()
            
            # Convertir a DataFrame
            data = response.data
            if not data:
                logger.warning(f"La tabla {table_name} está vacía.")
                return pd.DataFrame()
            
            return pd.DataFrame(data)
        except Exception as e:
            logger.error(f"Error descargando datos de {table_name}: {str(e)}")
            return pd.DataFrame()

    def _certify_and_log(self, report: Dict[str, Any], contract_yaml: Dict[str, Any]):
        """Publica el ticket en S3 y registra la auditoría detallada en Supabase."""
        client = self.db.get_service_client()
        try:
            # A. Publicar en Cloud Storage
            logger.info("   A. Publicando ticket en Storage...")
            cloud_path = self.certifier.publish_ticket(report)
            logger.info(f"      [OK] Ticket URI: {cloud_path}")
            
            # B. Registrar en sys_validation_contract
            logger.info("   B. Registrando auditoría de contrato...")
            contract_str = json.dumps(contract_yaml, sort_keys=True)
            contract_hash = hashlib.sha256(contract_str.encode()).hexdigest()
            db_status = "VALID" if report["status"] == "SUCCESS" else "INVALID"
            
            audit_record = {
                "contract_yaml": contract_str,
                "contract_hash": contract_hash, 
                "support_json": report, 
                "dvc_hash": report["tables"].get(self.mandatory_source, {}).get('semantic_hash', 'N/A'),
                "s3_pointer_uri": cloud_path,
                "total_tables": report["summary"].get("total", 0),
                "success_tables": report["summary"].get("valid", 0),
                "failed_tables": report["summary"].get("invalid", 0),
                "status": db_status
            }
            
            val_response = client.table(self.config['tables']['sys_validation_contract']).insert(audit_record).execute()
            validation_id = val_response.data[0]['id'] if val_response.data else None
            logger.info(f"      [OK] Validation ID: {validation_id}")

            # C. Actualizar sys_pipeline_execution
            logger.info("   C. Actualizando tracking de ejecución...")
            pipeline_record = {
                "id": report["execution_id"],
                "process_name": "unified_load_pipeline",
                "execution_mode": f"load:{report['load_type']}",
                "validation_id": validation_id,
                "status": "COMPLETED" if report["status"] == "SUCCESS" else "FAILED",
                "error_message": json.dumps(report["summary"]) if report["status"] == "FAILED" else None
            }
            client.table(self.config['tables']['sys_pipeline_execution']).upsert(pipeline_record).execute()
            logger.info("      [OK] Tracking actualizado.")

        except Exception as e:
            logger.error(f"Error en certificación/auditoría: {str(e)}")
            raise e

    def _determine_load_type(self, current_report: Dict[str, Any]) -> str:
        """Determina el tipo de carga basándose en el comportamiento de todas las tablas certificadas."""
        try:
            client = self.db.get_service_client()
            
            # 1. Verificar si es la primera carga válida de la historia
            response = client.table(self.config['tables']['sys_validation_contract'])\
                             .select("id")\
                             .eq("status", "VALID")\
                             .limit(1).execute()
            
            if not response.data:
                return "FULL (Initial)"

            # 2. Analizar estrategias de tablas que lograron certificarse en esta corrida
            certified_tables = [t for t in current_report.get("tables", {}).values() 
                               if t.get("certification_status") == "CERTIFIED"]
            
            strategies = [t.get("strategy") for t in certified_tables]
            
            # 3. Mapeo de Prioridades
            
            # A. Si cualquier tabla tuvo carga FULL, el sistema se refrescó
            if "FULL" in strategies:
                mandatory_strategy = current_report["tables"].get(self.mandatory_source, {}).get("strategy")
                if mandatory_strategy == "SKIP":
                    return "FULL (Partial Refresh)" # Novedades en secundarias, core estable
                return "FULL (Refresh/Re-load)"
            
            # B. Si no hubo FULL pero hubo carga INCREMENTAL
            if "INCREMENTAL" in strategies:
                return "INCREMENTAL"
            
            # C. Si absolutamente todas las tablas se saltaron
            return "NO_NEW_DATA"
                
        except Exception as e:
            logger.warning(f"No se pudo determinar el load_type: {str(e)}")
            return "FULL (Primary)"

    def _save_report(self, report: Dict[str, Any]):
        """Persiste el reporte de validación en la ruta configurada."""
        report_path = self.config['paths']['reports']['stage_load']['latest']
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=4)
        
        logger.info(f"Reporte de validación guardado en: {report_path}")

def main():
    parser = argparse.ArgumentParser(description="Bunuelos_TuRedondito Orchestrator CLI")
    parser.add_argument("command", choices=["load", "train", "forecast"], help="Comando a ejecutar")
    parser.add_argument("--config", default="config.yaml", help="Ruta al archivo de configuración")
    
    args = parser.parse_args()
    orchestrator = Orchestrator(args.config)
    
    if args.command == "load":
        orchestrator.load_data()
    else:
        logger.warning(f"El comando '{args.command}' aún no está implementado para la Etapa 2.1.")

if __name__ == "__main__":
    main()
