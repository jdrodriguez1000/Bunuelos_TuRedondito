# [PLAN-F02-01] - Implementation Plan: Validation & Ingest Certification (Stage 2.1)
**PROYECTO:** [Bunuelos_TuRedondito](./Project_Charter.md)  
**FASE:** Phase 2: MVP - Endogenous Variables  
**ESTATUS:** 🟢 FINALIZADO  
**VERSIÓN:** 1.2.0 (Synchronized with code)

---

## 1. CRONOGRAMA Y EQUIPO (Sprint Breakdown)

La Etapa 2.1 se ejecutará en **1 Micro-Sprint de 3 días** de desarrollo intensivo.

| Sprint | Enfoque | Entregable Clave |
| :--- | :--- | :--- |
| **S1.D1** | Infraestructura & CLI | Tablas Supabase y Orquestador `main.py` `[ARC-01]`. |
| **S1.D2** | Motor de Validación | `validator.py` con lógica INCREMENTAL y Semantic Hash `[DAT-01]`. |
| **S1.D3** | Certificación Cloud | Integración con S3 y Persistencia de Auditoría `[ARC-02]`. |

---

## 2. RUTA CRÍTICA (Critical Path)
1. **DB Setup**: Sin las tablas `sys_` no hay donde loguear el pipeline.
2. **Semantic Hash Logic**: Es la base del agnosticismo y la integridad en la nube.
3. **S3 Bridge**: Es el único punto de contacto con la siguiente etapa (2.2).

---

## 3. BACKLOG Y WBS (Work Breakdown Structure)

### 3.1 Infraestructura de Datos [DAT-01]
*   [x] **TASK-21-01**: Crear migración `apply_migration` para tablas `sys_validation_contract` y `sys_pipeline_execution`.
*   [x] **TASK-21-02**: Configurar `Storage` en Cloud (Supabase Bucket) para los `Validation Tickets`.

### 3.2 Desarrollo Core [ARC-01]
*   [x] **TASK-21-03**: Implementar CLI `main.py` con `argparse` y decoradores para manejo de errores globales.
*   [x] **TASK-21-04**: Implementar lógica de Detección de Modo (`FULL` vs `INCREMENTAL`) comparando el Hash del YAML y punteros en Supabase.
*   [x] **TASK-21-05**: Desarrollar `DataValidator` con métodos de perfilamiento extendido (**Cuartiles, IQR, % Categórico**).
*   [x] **TASK-21-09**: (**NEW**) Implementar **Fail-Safe Logic** (Blindaje) para contratos faltantes con registro de error en auditoría.

### 3.3 Integración y Despliegue [OBJ-04]
*   [x] **TASK-21-06**: Implementar `SemanticHashGenerator` (SHA-256 sobre metadatos y **Sample de Datos**).
*   [x] **TASK-21-07**: Desarrollar el adaptador de Cloud Storage para subir el `load_report.json` como ticket de autorización.
*   [x] **TASK-21-08**: Registrar el éxito final en `sys_pipeline_execution` con el FK al log de validación.

---

## 4. PLAN DE PRUEBAS (QA) [OBJ-04]

### 🧪 Pruebas Unitarias
*   `test_contract_drift`: Forzar un cambio en el YAML y verificar que el modo cambie de `INCREMENTAL` a `FULL`.
*   `test_fail_fast_type`: Enviar un string en una columna `numeric` y verificar excepción `ContractViolationError`.

### 🧪 Prueba de Humo (UAT)
1. Ejecutar `python main.py load`.
2. Verificar registro en Supabase con `status: VALID`.
3. Verificar existencia de ticket en S3.
4. Intentar una segunda ejecución inmediata y verificar que el modo sea `NO NEW DATA`.

---

## 5. RITOS DE GOBERNANZA
*   **Check-in Diario**: Validación de trazabilidad de los tags en los commits.
*   **Definición de Hecho (DoD)**: El código debe pasar `flake8` y tener cobertura de tests > 80% en los módulos de validación.

---
**Elaborado por:** Antigravity (MODO D: EL ORQUESTADOR)  
**Trazabilidad:** `[ARC-01]`, `[ARC-02]`, `[DAT-01]`, `[OBJ-04]`
