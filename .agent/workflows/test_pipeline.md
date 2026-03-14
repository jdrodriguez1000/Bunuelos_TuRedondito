---
description: Workflow para la ejecución y reporte de pruebas automatizadas (Pipeline de Calidad).
---

# WORKFLOW: Pipeline de Calidad (TEST_PIPELINE)

Este flujo automatiza la validación técnica del proyecto para garantizar la inmutabilidad de los datos.

## Pasos de Ejecución

### 1. Preparación y Limpieza
// turbo
Elimina cachés y residuos para garantizar una ejecución pura.
```powershell
if (Test-Path .pytest_cache) { Remove-Item -Recurse -Force .pytest_cache }
if (Test-Path tests/reports/tests_report_raw.json) { Remove-Item tests/reports/tests_report_raw.json }

# 1.1 Verificación de Integridad de Datos (DVC)
if (Get-Command dvc -ErrorAction SilentlyContinue) {
    Write-Host "Verificando sincronización de datos con DVC..."
    dvc status
}
```

### 2. Ejecución Jerárquica e Informe Crudo
// turbo
Ejecuta las pruebas (empezando por unitarias) y genera el JSON base.
```powershell
$env:PYTHONPATH="."; pytest tests/ --json-report --json-report-file=tests/reports/tests_report_raw.json
```

### 3. Consolidación de Reporte (Doble Persistencia)
// turbo
Transforma el reporte crudo en el formato oficial definido en la [[RULE-QA]](../../.agent/rules/testing_rules.md).
```powershell
if (Test-Path scripts/consolidate_reports.py) {
    python scripts/consolidate_reports.py
} else {
    Write-Warning "Script de consolidación no encontrado. Se omitirá este paso hasta su creación."
}
```

### 4. Archivado Histórico
// turbo
Garantiza la trazabilidad histórica de la salud del proyecto.
```powershell
if (Test-Path "tests/reports/tests_report.json") {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $HistoryDir = "tests/reports/history"
    if (-not (Test-Path $HistoryDir)) { New-Item -Path $HistoryDir -ItemType Directory }
    Copy-Item "tests/reports/tests_report.json" "$HistoryDir/tests_report_$timestamp.json"
    Write-Host "Vuelo histórico registrado."
}
```

---
> [!TIP]
> Puedes invocar este flujo mediante el comando `/test_pipeline` para validar cambios antes de cada commit.
