import os
import json
import logging
from typing import Dict, Any
from src.connector.db_connector import DBConnector

logger = logging.getLogger("CLOUD_CERTIFICATION")

class CloudCertifier:
    """
    Gestor de Certificación en la Nube (S3/Supabase Storage).
    Se encarga de persistir los 'Tickets de Autorización' (Reports) en el almacenamiento cloud.
    """

    def __init__(self):
        self.db = DBConnector()
        self.config = self.db.get_config()
        self.storage_config = self.config.get('paths', {}).get('cloud_storage', {})
        self.bucket_name = self.db.s3_config.get('bucket')

    def publish_ticket(self, report: Dict[str, Any]) -> str:
        """
        Sube el reporte de validación a Supabase Storage/S3.
        Actúa como el puente de autorización para las siguientes etapas.
        """
        prefix = self.storage_config.get('s3_tickets_prefix', 'tickets')
        filename = self.storage_config.get('s3_ticket_name', 'report.json')
        cloud_path = f"{prefix}/{filename}"

        try:
            logger.info(f"Subiendo ticket de certificación a: {self.bucket_name}/{cloud_path}...")
            
            # Convertir reporte a bytes/string
            report_data = json.dumps(report, indent=4).encode('utf-8')
            
            # Usar el cliente administrativo (Service Role) para saltar RLS en Storage si es necesario
            client = self.db.get_service_client()
            
            # Intentar subida (Update si existe, si no Upload)
            try:
                # Primero intentamos subir
                response = client.storage.from_(self.bucket_name).upload(
                    path=cloud_path,
                    file=report_data,
                    file_options={"content-type": "application/json", "x-upsert": "true"}
                )
            except Exception:
                # Si falla el upload con upsert (depende de la versión de la lib), intentamos remove + upload
                # pero el parámetro x-upsert suele funcionar en versiones recientes.
                logger.warning("Fallo en upload simple, intentando modo persistente...")
                client.storage.from_(self.bucket_name).remove([cloud_path])
                response = client.storage.from_(self.bucket_name).upload(
                    path=cloud_path,
                    file=report_data,
                    file_options={"content-type": "application/json"}
                )

            logger.info(f"✅ Ticket publicado exitosamente. Registro en nube: {cloud_path}")
            return cloud_path

        except Exception as e:
            logger.error(f"❌ Error publicando ticket en la nube: {str(e)}")
            raise e
