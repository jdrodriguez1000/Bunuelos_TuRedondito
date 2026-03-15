# [REQ-F02-02] - PRD: Ingesta Física y Almacenamiento Bronce (Stage 2.2)

**PROYECTO:** [Forecasting de Demanda de Buñuelos](./Project_Charter.md)  
**FASE:** Phase 2: MVP - Endogenous Variables `[PH-02]`  
**ETAPA:** Ingesta Física y Almacenamiento Bronce `[ST-02-02]`  
**ESTATUS:** 🔵 LISTO PARA REVISIÓN (Refinado por Workflow)  
**VERSIÓN:** 2.3.0

---

## 1. RESUMEN y ALINEACIÓN (Summary)
Este documento detalla los requerimientos para la **Ingesta Física** de datos desde Supabase hacia la **Capa Bronce (Landing)**. El componente `src/ingestor.py` actuará como el motor de sincronización que supera las limitaciones técnicas de la API (1000 filas) y garantiza la **Trazabilidad Total** mediante el uso de hashes semánticos y auditoría persistente.

### Alineación con el Project Charter:
*   **[OBJ-04] Eficiencia:** Automatizar la descarga y asegurar que la data esté lista para el modelado sin intervención manual.
*   **[REQ-01] Motor de Ingesta:** Implementación del primer módulo de carga batch escalable.
*   **[DAT-01] Fuentes de Datos:** Sincronización de las tablas diarias (Ventas, Inventario, Clima, etc.) definidas en el contrato.

---

## 2. ALCANCE ESPECÍFICO (Scope)

### ✅ Qué está INCLUIDO (In Scope)
*   **[REQ-22-01] Descarga Multi-Tabla Dinámica**: Descarga de tablas con flag `true` en el contrato que superaron la validación técnica.
*   **[REQ-22-02] Gestión de Batches (Pagination)**: Superación del límite de 1000 registros de la API de Supabase vía paginación por lotes.
*   **[REQ-22-03] Persistencia en Bronce (Parquet)**: Grabado de archivos inmutables `tabla_{semantic_hash}.parquet` en la carpeta `data/bronce/`.
*   **[REQ-22-04] Sincronización Remota Obligatoria**: Verificación de carga exitosa en el storage remoto (S3 vía DVC) antes de marcar éxito.
*   **[REQ-22-05] Configuración en `config.yaml`**: Frecuencias (D, M, Y), centinelas y reglas de negocio custom centralizadas.

### ❌ Qué está EXCLUIDO (Out of Scope)
*   Limpieza de datos (Null imputation) o transformaciones de formato de fecha (corresponden a la etapa Silver).

---

## 3. HISTORIAS DE USUARIO (User Stories)

| ID | Historia de Usuario | Etiquetas Relacionadas |
| :--- | :--- | :--- |
| **[US-22-01]** | Como **Analista de Datos**, quiero descargar tablas de más de 1000 registros para contar con el histórico completo de ventas desde 2017. | `[REQ-22-02]` `[OBJ-04]` |
| **[US-22-02]** | Como **Científico de Datos**, quiero que el nombre del archivo sea un hash semántico para que DVC solo rastree cambios cuando los datos reales cambien. | `[REQ-22-03]` `[BR-22-02]` |
| **[US-22-03]** | Como **Gerente de Producción**, quiero ver en un Dashboard si los datos de hoy están actualizados para confiar en el pronóstico del día. | `[REQ-22-12]` `[REQ-22-08]` |

---

## 4. INDICADORES DE SALUD Y AUDITORÍA (Dashboard Data)

El `ingestor.py` inyectará en la tabla `sys_ingestion_audit` un objeto JSONB diseñado para ser consumido por un **Dashboard de Alta Performance** basado en el stack:
*   **Frontend**: Next.js (React) + TypeScript (para tipado estricto de auditoría).
*   **Backend**: Node.js (Runtime de servidor).
*   **Consumo**: Acceso directo a Supabase via Client SDK.

*   **Identificación Técnica**: Status (SUCCESS/FAILED/NO_DATA), Row Count, Col Count.
*   **Evidence Snapshots**: Primeras 3 filas (**Head**), últimas 3 (**Tail**) y 3 **Random** para auditoría visual sin mover archivos pesados.
*   **Data Integrity Check**:
    *   **Data Leakage**: Alerta si hay registros con fecha >= Día X (Point-in-time).
    *   **Freshness / Lag**: Cálculo automático de retraso según frecuencia (Día X vs X-1).
    - **Gap Analysis**: Detección de fechas faltantes según `config.yaml`.
*   **Reglas de Negocio Custom**: Resultados de validaciones lógicas (ej. Suma de campos, valores > 0).

---

## 5. REGLAS DE NEGOCIO (Business Rules)

*   **[BR-22-01] Gatekeeper de Validación**: El `ingestor.py` solo opera sobre tablas cuya validación previa (`sys_validation_contract`) sea exitosa.
*   **[BR-22-02] Inmutabilidad Semántica**: El `semantic_hash` representa el dato, no el reporte. Si el dato no cambia, el hash persiste.
*   **[BR-22-03] Consistencia de Orquestación**: Cada ejecución debe actualizar obligatoriamente `sys_pipeline_execution`.

---

## 6. CRITERIOS DE ACEPTACIÓN (DoD)

1.  **Independencia Local**: El sistema puede reconstruir el estado en cualquier entorno (CI/CD) usando los hashes de Supabase + DVC Pull.
2.  **Visibilidad en Dashboard**: La salud técnica de N tablas es consultable vía SQL/Node.js sin procesar Parquets.
3.  **Trazabilidad Total**: Existe un vínculo 1:1 entre el `execution_id`, el registro en `sys_ingestion_audit` y el archivo físico en S3.

---
**Elaborado por:** Antigravity (Project Lifecycle Expert)  
**Fecha:** 2026-03-14  
