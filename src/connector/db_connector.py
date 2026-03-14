import os
import yaml
from typing import Optional
from supabase import create_client, Client
from dotenv import load_dotenv

class DBConnector:
    """
    Singleton Guard para la gestión centralizada de conexiones a Supabase y S3.
    Cumple con [REQ-CON-01], [REQ-ARC-01] y [D3.2] (Cero Hardcoding).
    """
    _instance: Optional['DBConnector'] = None
    _config: Optional[dict] = None
    _client: Optional[Client] = None
    _service_client: Optional[Client] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DBConnector, cls).__new__(cls)
            cls._instance._load_config()
            cls._instance._initialize()
        return cls._instance

    def _load_config(self):
        """Carga la configuración desde config.yaml [D3.2]."""
        config_path = os.path.join(os.getcwd(), "config.yaml")
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Archivo de configuración no encontrado en: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self._config = yaml.safe_load(f)

    def _get_env_var(self, key_path: list) -> str:
        """Helper para obtener variables de entorno definidas en el config."""
        env_var_name = self._config
        for key in key_path:
            env_var_name = env_var_name.get(key, {})
        
        if not isinstance(env_var_name, str):
            raise KeyError(f"No se pudo encontrar la ruta {key_path} en config.yaml o no es un string.")
            
        value = os.getenv(env_var_name)
        if not value:
            raise ValueError(f"La variable de entorno {env_var_name} no está definida.")
        return value

    def _initialize(self):
        """Inicialización perezosa de clientes [REQ-SEC-01]."""
        load_dotenv()
        
        # 1. Configuración de Supabase
        try:
            url = self._get_env_var(['database', 'supabase', 'env_url'])
            key = self._get_env_var(['database', 'supabase', 'env_key'])
            service_key = self._get_env_var(['database', 'supabase', 'env_service_key'])

            self._client = create_client(url, key)
            self._service_client = create_client(url, service_key)
        except (KeyError, ValueError) as e:
            print(f"⚠️ Aviso: Configuración de Supabase incompleta: {str(e)}")

        # 2. Configuración S3 (Opcional/Lazy) [REQ-S3-01]
        self.s3_config = {}
        try:
            self.s3_config = {
                "endpoint": self._get_env_var(['database', 'supabase', 's3', 'env_endpoint']),
                "access_key": self._get_env_var(['database', 'supabase', 's3', 'env_access_key']),
                "secret_key": self._get_env_var(['database', 'supabase', 's3', 'env_secret_key']),
                "region": self._get_env_var(['database', 'supabase', 's3', 'env_region']),
                "bucket": self._get_env_var(['database', 'supabase', 's3', 'env_bucket'])
            }
        except (KeyError, ValueError) as e:
            print(f"⚠️ Aviso: Configuración S3 incompleta o ausente: {str(e)}")

    def get_client(self) -> Client:
        """Retorna el cliente estándar con RLS activo [REQ-ARC-01]."""
        return self._client

    def get_service_client(self) -> Client:
        """Retorna el cliente administrativo (Service Role) [REQ-INF-03]."""
        return self._service_client

    def get_config(self) -> dict:
        """Retorna el diccionario de configuración completo."""
        return self._config

    def test_connection(self) -> bool:
        """
        Realiza un 'handshake' validando visibilidad de la tabla 'usr_ventas'.
        Trazabilidad: [REQ-VAL-01], [DAT-01], [MET-INF-01]
        """
        try:
            table_name = self._config['tables']['usr_ventas']
            response = self._client.table(table_name).select("count", count="exact").limit(1).execute()
            return True
        except Exception as e:
            print(f"Error de conexión [ERR_DB_001]: {str(e)}")
            return False
