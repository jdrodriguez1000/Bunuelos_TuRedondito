import os
import yaml
import json
import logging
import argparse
import pandas as pd
from datetime import datetime
from typing import Dict, Any

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
        
        # 0. Inicializar Resultados Holísticos (Preparado para fallos tempranos)
        execution_id = f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        load_report = {
            "execution_id": execution_id,
            "timestamp": datetime.now().isoformat(),
            "status": "SUCCESS",
            "load_type": "ORCHESTRATION_ERROR",
            "tables": {},
            "summary": {"total": 0, "valid": 0, "invalid": 0},
            "error_msg": None
        }
        data_contract = {}

        try:
            # 1. Ejecutar Ingestión Física y Auditoría de Salud (Stage 2.2)
            # Esto maneja batches, Parquet, Semantic Hashing y Health Audit.
            ingestion_summary = self.ingestor.run_full_ingestion()
            
            if ingestion_summary["failed"] > 0:
                logger.warning(f"⚠️ La ingestión terminó con {ingestion_summary['failed']} tablas fallidas.")

            # 2. Cargar Contrato de Datos con Blindaje (Legacy/Validation 2.1)
            # Mantenemos esto para compatibilidad con el reporte de validación estructural
            contract_path = self.config['contract']['path']
            try:
                data_contract = self._load_yaml(contract_path)
            except FileNotFoundError:
                error_txt = f"ERROR DE GOBIERNO: El contrato no existe en '{contract_path}'"
                logger.error(error_txt)
                load_report["status"] = "FAILED"
                load_report["error_msg"] = error_txt
                raise # Saltamos al bloque de persistencia final

            # 2. Iterar sobre fuentes habilitadas en el contrato
            for source in data_contract.get('data_sources', []):
                source_name = source['name']
                
                # Verificar si es obligatoria pero está deshabilitada
                if not source.get('enabled', False):
                    if source_name == self.mandatory_source:
                        logger.error(f"CRÍTICO: La fuente obligatoria '{self.mandatory_source}' está deshabilitada.")
                        load_report["status"] = "FAILED"
                    continue
                
                table_name = source['db_table']
                logger.info(f"Procesando fuente: {source_name} ({table_name})")
                
                # --- CARGA DE DATOS REAL ---
                df_real = self._fetch_from_supabase(table_name)
                # ---------------------------

                # 3. Validar Tabla
                table_contract = {'columns': {col: {'type': t} for col, t in source['schema'].items()}}
                report = self.validator.validate_table(table_name, df_real, table_contract)
                
                load_report["tables"][source_name] = report
                load_report["summary"]["total"] += 1
                
                if report["status"] == "VALID":
                    load_report["summary"]["valid"] += 1
                else:
                    load_report["summary"]["invalid"] += 1
                    load_report["status"] = "FAILED"

            # 4. Doble Check de Integridad
            if self.mandatory_source not in load_report["tables"] and load_report["status"] != "FAILED":
                 logger.error(f"CRÍTICO: La fuente obligatoria '{self.mandatory_source}' no fue procesada.")
                 load_report["status"] = "FAILED"

            # 5. Determinar Tipo de Carga
            if load_report["status"] == "SUCCESS":
                load_report["load_type"] = self._determine_load_type(load_report)
                logger.info(f"Tipo de Carga detectado: {load_report['load_type']}")
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
        try:
            # A. Publicar en Cloud Storage (S3/Supabase Storage)
            cloud_path = self.certifier.publish_ticket(report)
            
            # B. Registrar en Tabla de Auditoría sys_validation_contract
            client = self.db.get_service_client()
            
            # Ajustar estatus para cumplir con el CHECK de la base de datos (VALID/INVALID)
            db_status = "VALID" if report["status"] == "SUCCESS" else "INVALID"
            
            # Mapeo exacto al esquema SQL de scripts/sql/create_sys_audit_tables.sql
            audit_record = {
                "contract_yaml": json.dumps(contract_yaml),
                "contract_hash": report["execution_id"], 
                "support_json": report, 
                "dvc_hash": report["tables"].get(self.mandatory_source, {}).get('semantic_hash', 'N/A'),
                "s3_pointer_uri": cloud_path,
                "total_tables": report["summary"]["total"],
                "success_tables": report["summary"]["valid"],
                "failed_tables": report["summary"]["invalid"],
                "status": db_status
            }
            
            # Insertar y obtener el ID generado (returning='minimal' no devuelve, usamos execute().data)
            val_response = client.table(self.config['tables']['sys_validation_contract']).insert(audit_record).execute()
            validation_id = val_response.data[0]['id'] if val_response.data else None
            logger.info(f"Audit log persistido en sys_validation_contract (ID: {validation_id}).")

            # C. Registrar en Tabla de Seguimiento sys_pipeline_execution
            # NOTA: Usamos execution_mode = 'load:{type}' para dar visibilidad sin cambiar esquema si no es posible
            pipeline_record = {
                "process_name": "data_validation",
                "execution_mode": f"load:{report['load_type']}",
                "validation_id": validation_id,
                "status": "COMPLETED" if report["status"] == "SUCCESS" else "FAILED",
                "error_message": json.dumps(report["summary"]) if report["status"] == "FAILED" else None
            }
            
            client.table(self.config['tables']['sys_pipeline_execution']).insert(pipeline_record).execute()
            logger.info("Seguimiento de ejecución registrado en sys_pipeline_execution.")

        except Exception as e:
            logger.error(f"Error en certificación/auditoría: {str(e)}")
            raise e

    def _determine_load_type(self, current_report: Dict[str, Any]) -> str:
        """Determina si la carga es FULL, INCREMENTAL o NO_NEW_DATA comparando con la última válida."""
        try:
            client = self.db.get_service_client()
            # Buscar último registro válido
            response = client.table(self.config['tables']['sys_validation_contract'])\
                             .select("dvc_hash, support_json")\
                             .eq("status", "VALID")\
                             .order("created_at", desc=True)\
                             .limit(1).execute()
            
            if not response.data:
                return "FULL (Initial)"
            
            last_record = response.data[0]
            last_hash = last_record["dvc_hash"]
            # Extraer row_count de la fuente mandatoria del support_json del último registro
            last_support = last_record["support_json"]
            last_rows = last_support.get("tables", {}).get(self.mandatory_source, {}).get("row_count", 0)
            
            current_table_info = current_report["tables"].get(self.mandatory_source, {})
            current_hash = current_table_info.get("semantic_hash")
            current_rows = current_table_info.get("row_count", 0)
            
            if current_hash == last_hash:
                return "NO_NEW_DATA"
            elif current_rows > last_rows:
                return "INCREMENTAL"
            else:
                return "FULL (Refresh/Re-load)"
                
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
