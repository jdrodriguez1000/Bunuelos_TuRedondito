# [PLAN-F02-02] - Sprint Plan: Ingesta Física y Auditoría Bronce

**PROYECTO:** [Forecasting de Demanda de Buñuelos](../artifacts/Project_Charter.md)  
**FASE:** Phase 2: MVP - Endogenous Variables `[PH-02]`  
**ETAPA:** Ingesta Física y Almacenamiento Bronce `[ST-02-02]`  
**ESTATUS:** 📅 PLANIFICADO  
**VERSIÓN:** 1.0.0

---

## 1. OBJETIVO DEL SPRINT
Desplegar un motor de ingesta (`ingestor.py`) capaz de descargar N tablas de Supabase, validarlas físicamente contra indicadores de salud (Gaps, Leakage, Freshness) y persistirlas de forma inmutable en la nube (DVC/S3) con trazabilidad total en SQL.

---

## 2. ESTRUCTURA DE TAREAS (WBS) `[WBS-22]`

### Tanda 1: Infraestructura y Persistencia (Infra & DB)
*   **[TSK-22-01]** Configurar el entorno DVC para sincronización automática con el storage remoto.
*   **[TSK-22-02]** Actualizar `config.yaml` con parámetros de frecuencia y reglas custom por tabla.
*   **[TSK-22-03]** Crear script SQL de migración para la tabla `sys_ingestion_audit`.

### Tanda 2: Motor de Ingesta (Core Logic)
*   **[TSK-22-04]** Implementar `src/ingestor.py`: Crear `UnifiedIngestor` con lógica de paginación y **Motor de Estrategia Inteligente** (Incremental/Skip por punteros).
*   **[TSK-22-05]** Desarrollo en `src/ingestor.py`: Inmutabilidad vía hashing semántico y soporte de **Bootstrap (Hito 0)** con validación de emergencia.
*   **[TSK-22-06]** Desarrollar **Motor de Scoring Ponderado**:
    *   Cálculo de 4 dimensiones (Business, Continuity, Integrity, Cleaning).
    *   Detección de Gaps, Freshness, Leakage y reglas dinámicas vía `df.eval`.

### Tanda 3: Auditoría e Integración Dashboard
*   **[TSK-22-07]** Implementar la generación del `health_report` con muestras y **Dimensiones de Salud** para Dashboard.
*   **[TSK-22-08]** Integrar orquestación en `main.py`: Gestión de **Master Execution UUID** y Gatekeeper Global.
*   **[TSK-22-09]** Validar doble persistencia (Local y Cloud Ticket) con trazabilidad en `sys_pipeline_execution`.

---

## 3. CRONOGRAMA DE EJECUCIÓN (Hitos) `[HIT-22]`

| Hito | Entregable | Estimación (Dev Hours) |
| :--- | :--- | :--- |
| **M1: Persistence Ready** | Tabla de auditoría migrada y DVC configurado. | 2h |
| **M2: Batch Loading** | Descarga de >1000 registros funcionando. | 4h |
| **M3: Health Audit** | Reporte JSONB generado con Gaps y Freshness. | 6h |
| **M4: Integration** | Comando `python main.py load` operativo al 100%. | 2h |
| **TOTAL** | | **14h** |

---

## 4. ESTRATEGIA DE CALIDAD Y PRUEBAS `[QA-22]`

*   **Prueba de Carga**: Validar descarga de una tabla con >5000 registros (test de paginación).
*   **Prueba de Integridad**: Comparar conteo de filas en Supabase vs conteo en archivo Parquet descargado.
*   **Prueba de Trazabilidad**: Verificar que el ID de ejecución en `sys_pipeline_execution` coincida con el registro en `sys_ingestion_audit`.
*   **Prueba de Inmutabilidad**: Cambiar un registro en Supabase y confirmar que el `semantic_hash` cambia en el siguiente load.

---

## 5. DEPENDENCIAS Y RIESGOS `[RSK-22]`

| Riesgo | Impacto | Mitigación |
| :--- | :--- | :--- |
| Conexión intermitente con Supabase. | Alto | Reintentos (Exponential Backoff) en la paginación. |
| Datos con formatos inconsistentes de fecha. | Medio | Validación estricta antes del cálculo de Gaps. |
| Cuotas de storage S3 excedidas. | Bajo | Monitorización de tamaño de archivos Parquet (compresión snappy). |

---
**Planificado por:** Antigravity (Project Manager)  
**Fecha:** 2026-03-14  
