---
description: Flujo maestro para gestionar el ciclo de vida del proyecto (Charter, PRD, Spec, Plan).
---

# /manage_project

Este workflow automatiza la creación y seguimiento de la documentación core del proyecto utilizando la habilidad `project_lifecycle_expert`.

## Pasos

1. **Identificación de Necesidad**
   - **[A] Kickoff:** Crear Project Charter y, acto seguido, el Project Plan (Radar) basado en el Charter.
   - **[B] Formalización SDD:** Generar PRD, Spec o Plan de una Etapa.
   - **[C] Ejecución (Task List):** Generar el archivo granular `_task.md`.
   - **[D] Actualización del Radar:** Reflejar avances en el `project_plan.md`.

2. **Ejecución de Kickoff (Modo A + Modo B)**
   - Inicia entrevista del Charter.
   - Una vez aprobado el Charter, **genera automáticamente el `project_plan.md`** extrayendo las fases de la Dimensión 5 del Charter. Si no se especificaron fases ad-hoc, aplica las 7 fases estándar de forecasting.

3. **Ejecución de Documentación (Modo C, D o E)**
   - Pregunta Etapa y tipo de documento. Valida contra el Charter y el Plan.

4. **Ejecución de Task List (Modo F)**
   - Genera `docs/tasks/fXX_YY_task.md` con el detalle técnico de la etapa.

5. **Mantenimiento del Radar (Modo B Iterativo)**
   - Actualiza los estados de las fases en `project_plan.md` y marca la formalización de documentos SDD. **Mantiene el nivel estratégico sin bajar a tareas técnicas.**

6. **Refinamiento**
   - Asegura versionamiento y trazabilidad de tags.