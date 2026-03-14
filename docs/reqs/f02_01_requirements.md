# [REQ-F02-01] - PRD: Motor de Validación y Certificación de Ingesta (Stage 2.1)
**PROYECTO:** [Bunuelos_TuRedondito](./Project_Charter.md)  
**FASE:** Phase 2: MVP - Endogenous Variables  
**ESTATUS:** 🟢 FINALIZADO  
**VERSIÓN:** 1.1.0 (Refined by Workflow)

---

## 1. RESUMEN Y ALINEACIÓN (Executive Summary)
Este documento define los requerimientos para el **"Portero de Calidad"** del sistema, alineado con el objetivo de **Eficiencia [OBJ-04]** y **Objetividad [OBJ-03]** del Project Charter. La Etapa 2.1 construye la infraestructura de validación necesaria para asegurar que el MVP opere sobre datos certificados, eliminando el riesgo de "Garbage In, Garbage Out".

El propósito es implementar el comando `load` en el orquestador principal, que certificará la integridad de las tablas habilitadas en el contrato antes de autorizar cualquier descarga física de datos.

---

## 2. ALCANCE ESPECÍFICO (Scope)

### ✅ Qué está INCLUIDO (In Scope)
*   **[REQ-21-01] Orquestador CLI**: Implementación de `main.py` soportando el comando `load` para orquestación centralizada `[ARC-01]`.
*   **[REQ-21-02] Componente Validador (`validator.py`)**: Motor agnóstico capaz de validar N tablas según el `data_contract.yaml`.
*   **[REQ-21-03] Certificación en S3**: Almacenamiento de la evidencia de validación (Support JSON) en S3 como ticket de autorización para la ingesta.
*   **[REQ-21-04] Auditoría en Supabase**: Registro de ejecución y resultados en las tablas `sys_validation_contract` y `sys_pipeline_execution`.
*   **[REQ-21-05] Perfilamiento de Datos Extendido**: Cálculo de estadísticos robustos (Media, Std, Min, Max, **Cuartiles Q1/Q2/Q3**), detección de **Outliers con límites IQR** y análisis de **frecuencias relativas (%)** para categóricos.
*   **[REQ-21-06] Blindaje de Gobierno (Fail-Safe)**: Capacidad de detectar y registrar errores de configuración (ej. contrato inexistente) como `GOVERNMENT_ERROR` en la auditoría.

### ❌ Qué está EXCLUIDO (Out of Scope)
*   Descarga física de archivos Parquet (Corresponde a la sub-etapa 2.2).
*   Entrenamiento de modelos de Machine Learning.
*   Limpieza o imputación de datos nulos.

---

## 3. HISTORIAS DE USUARIO (User Stories)

| ID | Usuario | Necesidad | Propósito | Tag Vínculo |
| :--- | :--- | :--- | :--- | :--- |
| **US-21-01** | Data Engineer | Ejecutar `python main.py load`. | Iniciar el proceso de certificación de datos de forma automática. | `[ARC-01]` |
| **US-21-02** | Tech Lead | Que el validador detenga el proceso si una columna no coincide con el contrato. | Garantizar la integridad estructural de la fuente `[DAT-01]`. | `[REQ-01]` |
| **US-21-03** | Auditor de Datos | Consultar en Supabase/S3 el fingerprint semántico de los datos validados. | Asegurar la trazabilidad y reproducibilidad del experimento. | `[ARC-02]` |

---

## 4. REQUERIMIENTOS DE DATOS Y MODELADO (Business Rules)

*   **[BR-21-01] Contrato como Única Ley**: Ninguna tabla puede ser procesada si no está definida en el `data_contract.yaml`.
*   **[BR-21-02] Validación Atómica (Fail-Fast)**: Si una sola fuente de datos `enabled: true` falla, el contrato completo es **INVALID**.
*   **[BR-21-03] Gestión de Punteros Incremental**: El sistema debe comparar el puntero de evidencia en S3 contra la fuente en Supabase para determinar el modo: `FULL`, `INCREMENTAL` o `NO NEW DATA`.
*   **[BR-21-04] Detección de Deriva de Contrato**: Un cambio en el Hash del archivo YAML fuerza automáticamente una validación **FULL**.
*   **[BR-21-05] Huella Digital Semántica (Fingerprint)**: Generación de un hash en memoria de los datos validados para persistencia en `sys_validation_contract.dvc_hash`.
*   **[BR-21-06] Conversión Mandataria**: Los campos marcados como `datetime` deben ser convertibles exitosamente desde el origen (Supabase Object).
*   **[BR-21-07] Fuente Mandatoria (Anchor)**: La fuente definida en `config.yaml` como `mandatory_source` es obligatoria; si falta o está deshabilitada en el contrato, el proceso falla inmediatamente.
*   **[BR-21-08] Inmunidad de Fingerprint**: El Semantic Hash debe incluir una muestra física de datos (Sample Hash) para ser inmune a cambios de metadatos que no alteren el contenido.

---

## 5. INGENIERÍA (UX/Performance/Frecuencia)

*   **Output Técnico**: El sistema debe generar un archivo `load_report.json` local (doble persistencia) y su gemelo en S3.
*   **Performance**: La lectura para validación incremental debe ser optimizada mediante queries filtradas por el último puntero conocido si es posible.
*   **Frecuencia**: Diseñado para ejecución diaria (1:00 AM COT) según `[REQ-04]`.

---

## 6. CRITERIOS DE ACEPTACIÓN (DoD)

1.  **Orquestador Operativo**: El comando `load` ejecuta el flujo completo sin errores de sintaxis.
2.  **Certificación en Nube**: El registro en `sys_validation_contract` existe y contiene el `support_json` y el `dvc_hash` correcto.
3.  **Ticket en S3**: Existe un archivo en el bucket de S3 que autoriza la siguiente fase de descarga.
4.  **Agnosticismo Probado**: El validador procesa `inventory`, `sales` y `weather` dinámicamente sin nombres fijos en el código.
5.  **Fail-Fast**: Ante un error inducido en una columna, el sistema reporta `INVALID` y bloquea la fase 2.2.

---
**Elaborado por:** Antigravity (Project Lifecycle Expert)  
**Fecha:** 2026-03-14  
**Matriz de Trazabilidad:** `[OBJ-03]`, `[OBJ-04]`, `[REQ-01]`, `[DAT-01]`, `[ARC-01]`, `[ARC-02]`
