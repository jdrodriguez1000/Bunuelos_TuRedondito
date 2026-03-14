import time
import json
import os
import shutil
from datetime import datetime
from src.connector.db_connector import DBConnector

def run_performance_spike():
    """
    Measures connection latency and data visibility with Double Persistence.
    Trazabilidad: [MET-INF-01], [T-1.2-04], [RULE-QA]
    """
    print("--- [SPIKE] Iniciando Validación de Conector: Stage 1.2 ---")
    
    # 1. Instanciación (Carga config.yaml y .env automáticamente)
    start_time = time.time()
    try:
        connector = DBConnector()
        config = connector.get_config()
    except Exception as e:
        print(f"Error crítico cargando configuración: {e}")
        return

    # 2. Medición de Handshake
    handshake_start = time.time()
    success = connector.test_connection()
    handshake_end = time.time()
    
    total_latency_ms = (handshake_end - start_time) * 1000
    handshake_latency_ms = (handshake_end - handshake_start) * 1000
    
    # 3. Construcción del Reporte
    report_data = {
        "metadata": {
            "project": config['project']['name'],
            "stage": "1.2 - Database Connection",
            "timestamp": datetime.now().isoformat(),
            "agent": "Antigravity"
        },
        "metrics": {
            "total_latency_ms": round(total_latency_ms, 2),
            "handshake_latency_ms": round(handshake_latency_ms, 2),
            "handshake_success": success,
            "threshold_ms": config['network']['latency_threshold_ms']
        },
        "s3_check": "Configured" if hasattr(connector, 's3_config') else "Missing",
        "status": "PASS" if total_latency_ms < config['network']['latency_threshold_ms'] and success else "FAIL"
    }

    # 4. Doble Persistencia [RULE-QA]
    # Rutas desde config.yaml
    report_paths = config['paths']['reports']['stage_connector']
    latest_path = report_paths['latest']
    history_dir = report_paths['history']
    
    # Crear directorios
    os.makedirs(os.path.dirname(latest_path), exist_ok=True)
    os.makedirs(history_dir, exist_ok=True)

    # A. Guardar LATEST
    with open(latest_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=4, ensure_ascii=False)
    
    # B. Guardar HISTORICO (Timestamped)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    history_filename = f"connector_report_{timestamp}.json"
    history_path = os.path.join(history_dir, history_filename)
    
    shutil.copy2(latest_path, history_path)

    print(f"✅ Éxito: {success}")
    print(f"📊 Latencia: {total_latency_ms:.2f}ms")
    print(f"💾 Reporte LATEST: {latest_path}")
    print(f"💾 Reporte HISTORICO: {history_path}")

if __name__ == "__main__":
    run_performance_spike()
