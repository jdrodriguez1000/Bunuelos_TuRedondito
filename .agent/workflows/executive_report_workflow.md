---
description: Generación de reportes ejecutivos de alto impacto (Wow Factor) al finalizar cada fase.
---

# WORKFLOW: Storytelling Ejecutivo (STORYTELLING_WORKFLOW)

Transforma la data técnica en valor estratégico para el comité de **Bunuelos SAS**.

## 🎭 Contexto del Agente
> [!IMPORTANT]
> Para la ejecución de este flujo, asume el rol de **`forecasting_storyteller`**. 
> Tu misión es transformar la complejidad en claridad. Debes actuar como un consultor estratégico para la gerencia de **Buñuelos SAS**, eliminando cualquier rastro de lenguaje técnico o código y entregando hallazgos con el estándar visual **Bunuelos Premium**.

## Pasos del Workflow

### 1. Auditoría de Hitos Técnicos
- Escanear el estado final de la fase y extraer indicadores clave (Margen de Certeza, Calidad de Datos).

### 2. Visión de Datos
- Interpretar gráficas en `docs/artifacts/figures/` y validar contra las [Business Rules](../../.agent/rules/business_rules.md).

### 3. Síntesis Wow Factor
- Definir **Puntos de Poder** (Victorias) y **Verdades Críticas** (Acciones necesarias).

### 4. Generación del Reporte Ejecutivo
- Crear el archivo `docs/executive/phase_XX_YY_executive_latest.md` con paleta Premium y Cero Código.

### 5. Doble Persistencia
// turbo
Genera la traza histórica.
```powershell
$PhaseNum = if ($env:PHASE_NUM) { $env:PHASE_NUM } else { "01" } 
$StageNum = if ($env:STAGE_NUM) { $env:STAGE_NUM } else { "01" }
$Timestamp = Get-Date -Format "yyMMdd_HHmmss"
$LatestPath = "docs/executive/phase_$($PhaseNum)_$($StageNum)_executive_latest.md"
$HistoryPath = "docs/executive/history/phase_$($PhaseNum)_$($StageNum)_executive_$($Timestamp).md"

if (-not (Test-Path "docs/executive/history")) { New-Item -Path "docs/executive/history" -ItemType Directory }

if (Test-Path $LatestPath) {
    Copy-Item $LatestPath $HistoryPath -Force
    Write-Host "Histórico generado en: $HistoryPath"
} else {
    Write-Warning "No se encontró el reporte latest para archivar."
}
```

---

> [!TIP]
> Presenta siempre un resumen directo en el chat para el equipo Triple S al finalizar.