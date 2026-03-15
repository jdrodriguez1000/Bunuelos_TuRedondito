# Project Plan: Bunuelos_TuRedondito [MANDATO-TRAZABILIDAD]

## Executive Summary
This document outlines the execution roadmap for the demand forecasting system of **Bunuelos SAS**. Following the philosophies **"Less is More"**, **"Production First"**, and **"Spec-Driven Development (SDD)"**, we ensure that every development stage is preceded by robust documentation (REQ, SPEC, IMPL). This guarantees automation through Python modules (`src/`) and a MAPE < 15% using `skforecast`.

---

## 📈 Phase Execution Status

| Phase | Description | Status | Start Date | End Date |
| :--- | :--- | :--- | :--- | :--- |
| **01** | **Kickoff and Implementation** | **COMPLETED** | 2026-03-13 | 2026-03-14 |
| **02** | **Minimum Viable Product (MVP) - Endogenous Variables** | **IN PROGRESS** | 2026-03-14 | - |
| **03** | **Robustness - Calendar** | Pending | - | - |
| **04** | **Controllable Variables - Commercial & Marketing** | Pending | - | - |
| **05** | **External Non-Controllable Variables - Macro & Weather** | Pending | - | - |
| **06** | **"Black Swan" Events** | Pending | - | - |
| **07** | **Simulation & "What-If" Scenarios** | Pending | - | - |

---

## 🏗️ Detailed Phase 01: Kickoff and Implementation (COMPLETED)
**Objective:** Establish the project's technical skeleton, environment setup, and secure the data bridge with Supabase.

### Etapa 1.1: Infraestructura y Gobernanza (COMPLETADA)
- [x] Formalización de SDD: [REQ](../reqs/f01_01_requirements.md), [SPEC](../specs/f01_01_spec.md), [IMPL](../plans/f01_01_impl_plan.md).
- [x] Creación del Project Charter ([Project_Charter.md](Project_Charter.md)).
- [x] Definición de Reglas Globales y de Gobernanza ([.clinerules](../../.clinerules)).
- [x] Configuración del Índice Maestro ([index.md](../../index.md)).
- [x] Configuración de Entorno Virtual (Python 3.12+).
- [x] Creación de `requirements.txt` e instalación de dependencias.
- [x] Setup de Gobernanza (Reglas Técnicas, Skills, Workflows).
- [x] Estructura de Calidad (Carpeta `tests/` y Smoke Tests).
- [x] **Integración GitHub & CI**: Configuración de `ci_quality_gate.yml` y protección de rama `main`.
- [x] **Automatización de Releases**: Implementación de Google Release Please (`release_please.yml`).
- [x] **Lecciones Aprendidas**: Sistematización de hallazgos técnicos y de proceso.
- [x] **Resumen Ejecutivo (Phase 01)**: Generación de reporte Wow Factor de cierre de infraestructura.

### Stage 1.2: Database Connection (COMPLETED)
- [x] Refinement of SDD Documentation: [PRD](../reqs/f01_02_requirements.md)
- [x] Refinement of SDD Documentation: [SPEC](../specs/f01_02_spec.md).
- [x] Implementation Plan: [IMPL](../plans/f01_02_impl_plan.md).
- [x] **T-1.2-01**: Setup del Entorno Seguro (`.env.example` y validación de `.gitignore`).
- [x] **T-1.2-02**: Core Implementation: `DBConnector` (Singleton Guard Pattern) & `config.yaml`.
- [x] **T-1.2-03**: Proxy de Autenticación & S3: Implementación del Dual-Client (Std/Admin + S3 Config).
- [x] **T-1.2-04**: Spike de Desempeño: Medición de latencia y reporte `connector_report.json` (Doble Persistencia).
- [x] **T-1.2-05**: Suite de Pruebas Core: Unit & Integration Tests con QA Report.
- [x] **T-1.2-06**: Lecciones Aprendidas: Sistematización de hallazgos de conectividad y seguridad.
- [x] **T-1.2-07**: Resumen Ejecutivo (Stage 1.2): Generación de reporte de cierre "Wow Factor".

### Stage 1.3: Data Contract Creation (COMPLETED)
- [x] Refinement of SDD Documentation: [PRD](../reqs/f01_03_requirements.md), [SPEC](../specs/f01_03_spec.md).
- [x] Implementation Plan: [IMPL](../plans/f01_03_impl_plan.md).
- [x] **[T-1.3-01]** Creación física del archivo: `contracts/contracts/data_contract.yaml`.
- [x] **[T-1.3-02/03]** **Registro** de `inventory` e identificación de **variable target (`demanda_teorica_total`)**.
- [x] **[T-1.3-04]** Mapeo técnico de tipos (Supabase ↔ Pandas).
- [x] **[T-1.3-05]** Suite de Pruebas Unitarias para validación de arquitectura del contrato: `tests/unit/test_data_contract.py`.
- [x] **[T-1.3-06]** Sistematización de Lecciones Aprendidas (Mapeo Seminal): `docs/lessons_learned/lessons_learned_log.md`.
- [x] **[T-1.3-07]** **Resumen Ejecutivo (Stage 1.3)**: Alerta de riesgos por calidad de datos de origen (Cliente): `docs/executive/phase_01_03_executive_latest.md`.
- [x] **[T-1.3-08]** Sincronización de Plan y Commit Convencional.

---

## 🏗️ Detailed Phase 02: Minimum Viable Product (MVP) - Endogenous Variables (IN PROGRESS)
**Objective:** Build a robust forecasting baseline using internal historical sales data and technical demand variables.

### Stage 2.1: Data Validation & Ingest Certification (COMPLETED)
- [x] Refinement of SDD Documentation: [PRD](../reqs/f02_01_requirements.md), [SPEC](../specs/f02_01_spec.md), [IMPL](../plans/f02_01_impl_plan.md).
- [x] **[T-2.1-01] Motor de Validación (Validator Engine)**: Implementación de validación sintáctica y de integridad en `src/validator.py`.
- [x] **[T-2.1-02] Semantic Hash (Huella Digital)**: Implementación de algoritmos para detectar cambios en datos fuente y asegurar trazabilidad DVC-less.
- [x] **[T-2.1-03] Business Rule Profiling**: Cálculo automatizado de cuartiles, outliers (IQR), frecuencias y conteo de nulos por columna.
- [x] **[T-2.1-04] Cloud Certifier (Ingest Tickets)**: Implementación de `CloudCertifier` para publicación de evidencias de validación en Supabase Storage (S3).
- [x] **[T-2.1-05] Orquestación del comando `load`**: Integración en `main.py` para sincronizar validación, certificación y reporte.
- [x] **[T-2.1-06] Blindaje de CI/CD**: Refactorización de conectores y tests con Mocking para asegurar ejecuciones exitosas en GitHub Actions (Hotfixes).
- [x] **[T-2.1-07] QA Suite**: Suite completa de tests unitarios e integración (22 tests) con reporte de salud técnica.
- [x] **[T-2.1-08] Resumen Ejecutivo 2.1**: Generación de reporte estratégico "Wow Factor" y registro de Deuda Técnica.

### Stage 2.2: Physical Ingestion & Bronze Layer Storage (COMPLETED)
- [x] Formalización de SDD: [PRD](../reqs/f02_02_requirements.md), [SPEC](../specs/f02_02_spec.md), [PLAN](../plans/f02_02_plan.md).
- [x] **[T-2.2-01] Cloud-DVC Sync**: Configurar entorno DVC para sincronización obligatoria con storage remoto.
- [x] **[T-2.2-02] Configuración Estratégica**: Actualizar `config.yaml` con frecuencias y reglas custom.
- [x] **[T-2.2-03] Auditoría SQL**: Crear script de migración para la tabla `sys_ingestion_audit`.
- [x] **[T-2.2-04] Ingestor Core (`src/ingestor.py`)**: Implementar motor de descarga por batches (Supabase Bypass).
- [x] **[T-2.2-05] Hashing Inmutable (`src/ingestor.py`)**: Desarrollo de módulo de hashing semántico para persistencia Parquet.
- [x] **[T-2.2-06] Algoritmos de Salud**: Implementación de lógica para Gaps, Leakage y Freshness en el ingestor.
- [x] **[T-2.2-07] Dashboard Payload**: Generación de `health_report` (JSONB) con muestras (Head/Tail/Random).
- [x] **[T-2.2-08] Orquestación Load**: Integración de `src/ingestor.py` en `main.py`.
- [x] **[T-2.2-09] Cierre de Etapa**: Sistematización de Lecciones Aprendidas y Reporte Ejecutivo Wow Factor.

### Other Stages (Abbreviated)
*   **Stage 2.3: Training and Modeling (PENDING)**
*   **Stage 2.4: Invisibility & Inference (PENDING)**
*   **Stage 2.5: Dashboard MVP (PENDING)**

---

## 🔮 Future Phases Overview
*   **Phase 03: Robustness - Calendar:** Feriados, fienes de semana, quincenas y prima legal.
*   **Phase 04: Controllable Variables:** Promociones 2x1 e inversión en Marketing Digital (Ads).
*   **Phase 05: External Non-Controllable Variables:** Clima (precipitación) y variables macro (IPC, TRM, etc.).
*   **Phase 6: "Black Swan" Events:** Tratamiento de la pandemia y resiliencia ante anomalías.
*   **Phase 7: Simulation & "What-If" Scenarios:** Motor de escenarios dinámicos.

---

## 🎯 Hitos (Milestones)
1. **M1 (Infraestructura Lista):** Todos los directorios y documentos base establecidos.
2. **M2 (Conexión Establecida):** Extracción de datos exitosa desde Supabase.
3. **M3 (Contrato de Datos Firmado):** Esquemas validados para el inicio del MVP.
4. **M4 (Baseline Endógeno):** Primer modelo operativo con métricas de error.
5. **M5 (MVP Entregado):** Dashboard funcional y reporte ejecutivo.

---
*Last Edited: 2026-03-14*
