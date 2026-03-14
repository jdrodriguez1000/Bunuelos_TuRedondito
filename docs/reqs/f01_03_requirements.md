# [REQ-F01-03] - PRD: Creación del Contrato de Datos (Stage 1.3)
**ESTATUS:** 🟢 COMPLETADO

## 1. RESUMEN Y ALINEACIÓN (Overview & Alignment)

### Propósito específico de esta Fase
Establecer la **definición semántica y estructural** de los datos que alimentarán el motor de forecasting de **Bunuelos SAS**. El objetivo de esta etapa es crear un contrato formal que sirva como "Acuerdo de Nivel de Datos" (SLA), definiendo exactamente qué tablas y columnas son necesarias, sus tipos y sus llaves primarias. 

Este contrato actúa como el plano técnico para todas las validaciones posteriores y es la base para lograr el objetivo de **Precisión [OBJ-01]** y **Eficacia [OBJ-04]** del pronóstico mediante una entrada de datos limpia y tipificada.

### Tabla de Trazabilidad de la Fase
| Entregable | Objetivos Vinculados [OBJ-XX] | Requerimientos de Alto Nivel [REQ-XX] |
| :--- | :--- | :--- |
| **[DEL-01-03]** Manual Data Contract | **[OBJ-01]** Precisión < 15% MAPE<br>**[OBJ-04]** Automatización de Agrupación | **[REQ-INF-01]** Centralización en Supabase<br>**[REQ-DAT-01]** Integridad de Fuentes |

---

## 2. ALCANCE ESPECÍFICO DE LA FASE (Scope)

### Qué está INCLUIDO (In Scope)
*   **[REQ-CTR-01] Registro Manual del Contrato**: Creación del archivo `contracts/contracts/data_contract.yaml` para registrar las fuentes de datos.
*   **[REQ-CTR-02] Mapeo de Identidad Semántica**: Definición de alias de negocio (`name`) vinculados a tablas físicas de Supabase (`db_table`).
*   **[REQ-CTR-03] Tipificación Estricta**: Definición de tipos de datos para evitar errores de casting en el pipeline.
*   **[REQ-CTR-04] Registro de Fuentes Maestras**: Registro de las tablas `inventory`, `sales` y `weather`. Se deben registrar sus columnas estructurales, tipos y llaves primarias.
*   **[REQ-CTR-05] Blindaje de Variable Objetivo**: Identificación explícita de `demanda_teorica_total` en la tabla de inventario.

### Qué está EXCLUIDO (Out of Scope)
*   Validación automatizada o "Quality Guardrail" (Stage 2.1).
*   Consumo de datos o extracción (Stage 2.2).
*   Generación de perfiles estadísticos (Profiling).

---

## 3. CASOS DE USO Y ÉPICAS (User Stories & Epics)

### Épica: Definición Semántica de Datos [EP-03]
*   **User Story 1 (Data Governance):** Como **Ingeniero de Datos**, quiero definir manualmente el contrato para asegurar que solo las columnas necesarias y con los tipos correctos entren en el pipeline de forecasting.
*   **User Story 2 (Business Alignment):** Como **Analista de Negocio**, quiero que el contrato use nombres comprensibles (ej. `inventory`) aunque en la base de datos tengan nombres técnicos diferentes (ej. `inventario_detallado`).
*   **User Story 3 (Data Integrity):** Como **Arquitecto de Solución**, quiero que el contrato especifique claramente la `primary_key` para evitar duplicidad de registros en etapas posteriores.

---

## 4. REQUERIMIENTOS DE DATOS (Data Requirements)

### Mapeo de Tipos de Datos (Supabase vs Pandas)
Para asegurar la integridad semántica, el contrato utilizará tipos estándar que se mapearán de la siguiente forma:

| Tipo en Contrato | Origen (Supabase / Postgres) | Destino (Pandas / Python) |
| :--- | :--- | :--- |
| `datetime` | `date`, `timestamp`, `timestamptz` | `datetime64[ns]` |
| `int` | `integer`, `bigint`, `smallint` | `int64` |
| `float` | `numeric`, `double precision`, `real` | `float64` |
| `string` | `text`, `varchar`, `uuid` | `object` / `string` |
| `boolean` | `boolean` | `bool` |

### Mapeo de Fuentes Primarias [DAT-XX]
1.  **Inventario Detallado [DAT-03]**:
    - **Importancia**: Fuente maestra con la **variable target (`demanda_teorica_total`)**.
    - **Registro**: `usr_inventario_detallado` (Supabase) -> `inventory` (Contract).
2.  **Ventas Reales [DAT-04]**:
    - **Importancia**: Histórico de transacciones para validación de demanda.
    - **Registro**: `usr_ventas` (Supabase) -> `sales` (Contract).
3.  **Clima Diario [DAT-05]**:
    - **Importancia**: Variables exógenas (temperatura, lluvia) para el modelo.
    - **Registro**: `usr_clima_diario` (Supabase) -> `weather` (Contract).

---

## 5. REGLAS DE NEGOCIO Y GOBERNANZA
*   **BR-03-01 (Manual First)**: La creación del contrato es una decisión arquitectónica para garantizar el gobierno de datos manual; no se permiten generadores automáticos en esta fase.
*   **BR-03-02 (Atomic PK)**: Cada tabla en el contrato **DEBE** tener una llave primaria explícita que garantice la integridad referencial.
*   **BR-03-03 (Single Point of Truth)**: Solo lo registrado en `data_contract.yaml` será procesado por el pipeline de la Fase 2.

---

## 6. CRITERIOS DE ACEPTACIÓN (DoD)

### Definición de Hecho (Definition of Done)
1.  **Existencia del Artefacto**: Archivo `contracts/contracts/data_contract.yaml` disponible.
2.  **Validación de Schema**: Inclusión de las fuentes `inventory`, `sales` y `weather` con sus esquemas completos según DDL.
3.  **Matriz de Trazabilidad**: El contrato permite vincular cada tabla técnica con un alias de negocio definido en el Project Charter.
4.  **Aprobación Documental**: El PRD y SPEC de la fase están sincronizados y aprobados.

---
*Refinado por Antigravity (Modo B: Estratega de Producto) | 2026-03-14*
