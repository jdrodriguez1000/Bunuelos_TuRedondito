import json
import os
from datetime import datetime

RAW_REPORT = "tests/reports/tests_report_raw.json"
OFFICIAL_REPORT = "tests/reports/tests_report.json"

def consolidate():
    if not os.path.exists(RAW_REPORT):
        print(f"Error: {RAW_REPORT} no encontrado.")
        return

    with open(RAW_REPORT, 'r') as f:
        raw_data = json.load(f)

    consolidated = []
    
    # Agrupar por tipo (unit, integration) basándonos en la ruta
    suites = {
        "Unitaria": [t for t in raw_data.get('tests', []) if 'tests/unit' in t['nodeid']],
        "Integración": [t for t in raw_data.get('tests', []) if 'tests/integration' in t['nodeid']]
    }

    for suite_name, tests in suites.items():
        if not tests:
            continue
            
        suite_status = "PASSED"
        test_list = []
        
        for t in tests:
            raw_outcome = t.get('outcome', 'failed').upper()
            status = raw_outcome if raw_outcome in ["PASSED", "FAILED", "SKIPPED"] else "FAILED"
            
            if status == "FAILED":
                suite_status = "FAILED"
            
            test_list.append({
                "name": t['nodeid'],
                "status": status,
                "duration": round(t.get('setup', {}).get('duration', 0) + 
                                 t.get('call', {}).get('duration', 0) + 
                                 t.get('teardown', {}).get('duration', 0), 4)
            })

        consolidated.append({
            "type": suite_name,
            "status": suite_status,
            "timestamp": datetime.now().isoformat(),
            "details": f"Resultados de la suite {suite_name}",
            "summary": {
                "total": len(tests),
                "passed": len([t for t in test_list if t['status'] == "PASSED"]),
                "failed": len([t for t in test_list if t['status'] == "FAILED"]),
                "skipped": len([t for t in test_list if t['status'] == "SKIPPED"])
            },
            "tests": test_list
        })

    with open(OFFICIAL_REPORT, 'w', encoding='utf-8') as f:
        json.dump(consolidated, f, indent=4)
    
    print(f"✅ Reporte consolidado creado en: {OFFICIAL_REPORT}")

if __name__ == "__main__":
    consolidate()
