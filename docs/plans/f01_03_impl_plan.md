# [IMPL-F01-03] - Implementation Plan: Data Contract Creation (Stage 1.3)
**ESTATUS:** 🟢 COMPLETADO

Este documento detalla la hoja de ruta táctica para ejecutar el **registro manual** de las fuentes de datos en el contrato maestro de **Bunuelos_TuRedondito**, alineado con el **[SPEC-F01-03]** y asegurando la integridad de la variable target.

---

## 1. RESUMEN DEL CRONOGRAMA Y EQUIPO (Timeline & Resources)
*   **Sprint Asociado:** Sprint 1: Conectividad y Blindaje.
*   **Duración Estimada:** 1 Sesión (Foco en Gobernanza Semántica).
*   **Roles Ejecutores:**
    *   **Data Engineer (AI/Antigravity):** Registro de esquemas y mapeo de tipos Pandas.
    *   **Data Architect (AI/Antigravity):** Validación de la estructura jerárquica del YAML.
    *   **Product Owner (User):** Confirmación de las 15 columnas de inventario y variable target.

---

## 2. RUTA CRÍTICA Y DEPENDENCIAS (Critical Path)
*   **Bloqueador Principal:** Ninguno (Es una actividad de definición manual).
*   **Dependencia:** La validación automática de datos (Stage 2.1) depende totalmente de la completitud de este registro.
*   **Foco Estratégico:** El registro de la columna `demanda_teorica_total` es el "corazón" del contrato, ya que define el objetivo del modelo de ML.

---

## 3. PRODUCT BACKLOG Y WBS (Work Breakdown Structure)

### Épica: Definición Semántica de Datos [EP-03]
| ID | Tarea | Descripción | Status | Responsable | Etiqueta |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **[T-1.3-01]** | Infraestructura de Contratos | Creación del directorio `contracts/contracts/` y archivo `data_contract.yaml`. | [x] | Data Engineer | **[REQ-CTR-01]** |
| **[T-1.3-02]** | Registro de Fuente Maestra | Registro de `inventory`, `sales` y `weather` en el YAML. | [x] | Data Architect | **[REQ-CTR-04]** |
| **[T-1.3-03]** | Mapeo de Variable Target | Inclusión de `demanda_teorica_total` con tipo `int`. | [x] | Data Engineer | **[REQ-CTR-04]** |
| **[T-1.3-04]** | Tipificación Pandas | Aplicación de la matriz de tipos técnica (Supabase ↔ Pandas). | [x] | Data Engineer | **[REQ-CTR-03]** |
| **[T-1.3-05]** | QA: Suite de Pruebas | Implementación de `tests/unit/test_data_contract.py`. | [x] | QA Engineer | **[RULE-QA]** |
| **[T-1.3-06]** | QA: Ejecución Pipeline | Ejecución de `/test_pipeline` y reporte con Doble Persistencia. | [x] | QA Engineer | **[RULE-QA]** |
| **[T-1.3-07]** | Lecciones Aprendidas | Sistematización de aprendizajes en `LESSONS_LEARNED.md`. | [x] | Tech Lead | **[RULE-LL]** |
| **[T-1.3-08]** | Reporte Ejecutivo | Generación de reporte Wow Factor e identificación de riesgos. | [x] | PM | **[RULE-COM]** |

---

## 4. PLANIFICACIÓN POR SPRINTS (Sprint Roadmap)

### Sprint 1: Conectividad y Blindaje (Current)
*   **Objetivo del Sprint:** Establecer la "Verdad Semántica" del proyecto mediante un contrato de datos manual y tipificado.
*   **Entregables Críticos:**
    *   `contracts/contracts/data_contract.yaml` con las fuentes `inventory`, `sales` y `weather` registradas.
    *   Identificación clara de la variable objetivo y su llave primaria (`fecha`).

---

## 5. PLAN DE PRUEBAS Y UAT (Quality Assurance)

### Pruebas Técnicas
*   **Sintaxis YAML:** Verificación de que el archivo no contenga errores de indentación o caracteres especiales prohibidos.
*   **Integridad de Mapeo:** Confirmar que `db_table` coincida con los nombres físicos en Supabase.

### UAT (Aceptación de Negocio)
*   **Validación de Negocio:** El usuario confirma que las 15 columnas registradas en el contrato son las necesarias para el cálculo de la demanda.

---

## 6. RITOS ÁGILES Y GOBERNANZA

### Definition of Done (DoD) de la Fase
*   Archivo de contrato disponible en la ruta especificada.
*   Registro completo de las tablas `inventory`, `sales` y `weather`.
*   Variable target `demanda_teorica_total` definida y tipificada como `int`.
*   Trazabilidad completa con el **[PRD-F01-03]**.

---
> [!IMPORTANT]
> **Aviso de Gobernanza:** Este contrato es manual por diseño para garantizar que solo los datos validados por el negocio entren al pipeline. No se permite la generación automática de este archivo.

*Plan refinado por Antigravity (Modo D: Orquestador de Entrega) | 2026-03-14*
