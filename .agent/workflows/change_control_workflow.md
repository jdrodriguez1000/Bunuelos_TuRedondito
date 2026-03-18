---
description: Gestión profesional de solicitudes de cambio para documentos aprobados.
---

# WORKFLOW: Gestión de Control de Cambios (CHANGE_CONTROL)

Este workflow garantiza que cualquier modificación al proyecto sea trazable, aprobada y consistente en toda la documentación (Efecto Dominó).

## 🎭 Contexto del Agente
> [!IMPORTANT]
> Para la ejecución de este flujo, asume el rol de **`change_manager_pm`**. 
> Tu misión es actuar como el guardián de la **Baseline** del proyecto. Debes prevenir el "Scope Creep" y asegurar que ninguna modificación rompa la **Trazabilidad Atómica**. Aplica el **Método de Operación** de tu habilidad en cada paso.


## Pasos del Workflow

### 1. Recepción y Clasificación
- **Acción**: Identificar la solicitud y clasificarla (Menor vs Mayor) usando `change_control_rules.md`.

### 2. Análisis de Impacto (Sólo Cambios Mayores)
- **Acción**: Escanear documentos para identificar dependencias.
- **Salida**: Informar al usuario sobre los efectos secundarios del cambio.

### 3. Creación de la Solicitud de Cambio (CR)
// turbo
Genera el documento formal en `docs/control_changes/`.
```powershell
$PathCC = "docs/control_changes"
if (-not (Test-Path $PathCC)) { New-Item -Path $PathCC -ItemType Directory }

$CR_ID = "CR_$(Get-Date -Format 'MM_dd_HHmm')"
$PathCR = "$PathCC/$($CR_ID).md"

$CR_Template = @"
# Solicitud de Cambio (Change Request) - $($CR_ID)
## Proyecto: Bunuelos_TuRedondito - Bunuelos SAS
### [Título descriptivo del cambio]

**Estado**: PENDIENTE
**Fecha**: $(Get-Date -Format 'yyyy-MM-dd')
**Autor**: Antigravity (AI Agent)

---

## 1. DESCRIPCIÓN DEL CAMBIO
[Describir qué cambia y por qué. Referenciar IDs afectados ej. REQ-F01-01]

---

## 2. IMPACTO EN ARTEFACTOS Y CÓDIGO
| Artefacto | Versión | Ajuste |
| :--- | :--- | :--- |
| [Ej. project_charter.md] | [vX.X] | [Descripción] |

---

## 3. VALIDACIÓN Y CIERRE
[Criterios para dar por cerrado el cambio]
---
**Autoridad de Configuración**: Change Manager PM (Antigravity)
"@

New-Item -Path $PathCR -Value $CR_Template -ItemType File
Write-Host "CR creada en: $PathCR"
```

### 4. Actualización del Project Charter (Change Log)
- **Acción**: Agregar entrada en el "Registro de Cambios" del `Project_Charter.md` e incrementar versión.

### 5. Propagación en Cascada
- **Acción**: Actualizar PRDs, SPECs y Plans vinculados.

### 6. Verificación de Trazabilidad
- **Acción**: Validar la Matriz de Trazabilidad.

### 7. Confirmación y Sincronización
- **Acción**: Resumen de cambios y sincronización con GitHub si está configurado.