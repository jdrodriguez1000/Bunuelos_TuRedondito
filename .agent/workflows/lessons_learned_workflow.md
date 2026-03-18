---
description: Workflow para la captura y sistematización de aprendizajes del proyecto.
---

# WORKFLOW: Gestión de Lecciones Aprendidas (LEARN_FLOW)

Este flujo se ejecuta al final de cada fase o después de resolver un incidente crítico.

## 🎭 Contexto del Agente
> [!IMPORTANT]
> Para la ejecución de este flujo, asume el rol de **`lessons_learned_expert`**. 
> Tu misión es institucionalizar el conocimiento. No te limites a describir "qué pasó"; utiliza tu capacidad de **Reflexión Crítica** y **Análisis de Causa Raíz** para entender el "por qué". Cada entrada en el log debe ser accionable y mantener la **Trazabilidad** con los IDs del proyecto.

## Pasos del Workflow

### 1. Auditoría de Experiencia
Analizar los últimos logs de ejecución y feedback:
- ¿Hubo retrabajos significativos?
- ¿Se malinterpretó alguna regla de negocio?
- ¿Qué herramienta o enfoque funcionó excepcionalmente bien?

### 2. Clasificación del Hallazgo
Categorizar según [[RULE-LEARN]](../../.agent/rules/lessons_learned_rules.md) (TECHNICAL, BUSINESS, PROCESS).

### 3. Registro en el Log
Actualizar el archivo `docs/lessons_learned/lessons_learned_log.md`.
// turbo
```powershell
$LogPath = "docs/lessons_learned/lessons_learned_log.md"
$Dir = "docs/lessons_learned"
if (-not (Test-Path $Dir)) { New-Item -Path $Dir -ItemType Directory }
if (-not (Test-Path $LogPath)) { New-Item -Path $LogPath -Value "# LOG DE LECCIONES APRENDIDAS - BUNUELOS_TUREDONDITO`n`n" -ItemType File }
Write-Host "Log listo para edición."
```

### 4. Propagación de Conocimiento
Si la lección implica un cambio en las Reglas Globales, Técnicas o de Negocio:
- Activar el `/change_control_workflow` para actualizar las reglas correspondientes.

### 5. Cierre de Ciclo
Confirmar al usuario que el aprendizaje ha sido institucionalizado en el sistema de gestión del conocimiento.