import json
import os
from datetime import datetime

def consolidate():
    raw_path = 'tests/reports/tests_report_raw.json'
    output_path = 'tests/reports/tests_report.json'
    history_dir = 'tests/reports/history'
    
    if not os.path.exists(raw_path):
        print(f"Error: {raw_path} no encontrado.")
        return

    with open(raw_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    # Transformar al formato oficial [RULE-QA]
    consolidated = []
    
    # Clasificar tests por tipo basándose en su ruta
    suites = {
        "Unitaria": [],
        "Integración": [],
        "Funcional": []
    }
    
    for test in raw_data.get('tests', []):
        nodeid = test.get('nodeid', '')
        status = test.get('outcome', 'failed').upper()
        test_info = {"name": nodeid, "status": status}
        
        if 'unit' in nodeid:
            suites["Unitaria"].append(test_info)
        elif 'integration' in nodeid:
            suites["Integración"].append(test_info)
        elif 'functional' in nodeid:
            suites["Funcional"].append(test_info)

    for suite_type, tests in suites.items():
        if tests:
            passed = sum(1 for t in tests if t['status'] == 'PASSED')
            failed = sum(1 for t in tests if t['status'] == 'FAILED')
            skipped = sum(1 for t in tests if t['status'] == 'SKIPPED')
            
            suite_status = "PASSED" if failed == 0 else "FAILED"
            
            consolidated.append({
                "type": suite_type,
                "status": suite_status,
                "timestamp": datetime.now().isoformat(),
                "details": f"Resultados de la suite {suite_type}",
                "summary": {
                    "total": len(tests),
                    "passed": passed,
                    "failed": failed,
                    "skipped": skipped
                },
                "tests": tests
            })

    # Guardar Latest
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(consolidated, f, indent=2)
    
    # Doble Persistencia: Histórico (ya manejado por el workflow de powershell en este caso, 
    # pero podemos hacerlo aquí para ser redundantes o dejar que el workflow lo haga)
    # Según workflow, el .ps1 lo hace. Pero RULE-QA dice "Automatización del archivado... tras cada ejecución".
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs(history_dir, exist_ok=True)
    history_path = os.path.join(history_dir, f"tests_report_{timestamp}.json")
    with open(history_path, 'w', encoding='utf-8') as f:
        json.dump(consolidated, f, indent=2)

    print(f"✅ Reporte consolidado y archivado: {output_path}")

if __name__ == "__main__":
    consolidate()
