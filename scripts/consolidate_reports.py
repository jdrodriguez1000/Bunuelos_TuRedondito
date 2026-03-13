import json
import os
from datetime import datetime

def consolidate():
    raw_path = "tests/reports/tests_report_raw.json"
    final_path = "tests/reports/tests_report.json"
    
    if not os.path.exists(raw_path):
        print("No se encontró el reporte crudo.")
        return

    with open(raw_path, 'r') as f:
        raw_data = json.load(f)

    # Estructura simplificada para el reporte oficial Bunuelos SAS
    report = [
        {
            "type": "Ejecución Automática",
            "status": "PASSED" if raw_data.get("exitcode") == 0 else "FAILED",
            "timestamp": datetime.now().isoformat(),
            "summary": raw_data.get("summary", {}),
            "tests": [
                {
                    "name": t["nodeid"],
                    "status": t["outcome"].upper()
                } for t in raw_data.get("tests", [])
            ]
        }
    ]

    with open(final_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"Reporte consolidado en: {final_path}")

if __name__ == "__main__":
    consolidate()
