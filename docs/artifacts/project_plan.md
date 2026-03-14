# Project Plan: Bunuelos_TuRedondito [MANDATO-TRAZABILIDAD]

## Executive Summary
This document outlines the execution roadmap for the demand forecasting system of **Bunuelos SAS**. Following the philosophies **"Less is More"**, **"Production First"**, and **"Spec-Driven Development (SDD)"**, we ensure that every development stage is preceded by robust documentation (REQ, SPEC, IMPL). This guarantees automation through Python modules (`src/`) and a MAPE < 15% using `skforecast`.

---

## 📈 Phase Execution Status

| Phase | Description | Status | Start Date | End Date |
| :--- | :--- | :--- | :--- | :--- |
| **01** | **Kickoff and Implementation** | **IN PROGRESS** | 2026-03-13 | TBD |
| **02** | **Minimum Viable Product (MVP) - Endogenous Variables** | Pending | - | - |
| **03** | **Robustness - Calendar** | Pending | - | - |
| **04** | **Controllable Variables - Commercial & Marketing** | Pending | - | - |
| **05** | **External Non-Controllable Variables - Macro & Weather** | Pending | - | - |
| **06** | **"Black Swan" Events** | Pending | - | - |
| **07** | **Simulation & "What-If" Scenarios** | Pending | - | - |

---

## 🏗️ Detailed Phase 01: Kickoff and Implementation (IN PROGRESS)
**Objective:** Establish the project's technical skeleton, environment setup, and secure the data bridge with Supabase.

### Etapa 1.1: Infraestructura y Gobernanza (EN PROCESO)
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
- [ ] **Lecciones Aprendidas**: Sistematización de hallazgos técnicos y de proceso.
- [ ] **Resumen Ejecutivo (Phase 01)**: Generación de reporte Wow Factor de cierre de infraestructura.

### Stage 1.2: Database Connection (PENDING)
- [ ] Refinement of SDD Documentation: [PRD](../reqs/f01_02_requirements.md), [SPEC](../specs/f01_02_spec.md).
- [ ] Secure environment configuration (`.env`).
- [ ] Implementation of `DBConnector` (Singleton Pattern).
- [ ] Validation of Pipeline Quality (Unit & Integration Tests).
- [ ] Connection test success and latency validation.

### Stage 1.3: Data Contract Creation (PENDING)
- [ ] Refinement of SDD Documentation: [PRD](../reqs/f01_03_requirements.md), [SPEC](../specs/f01_03_spec.md).
- [ ] Setup of `config.yaml` for 9 data sources.
- [ ] Development of `Introspector` and `StatsEngine`.
- [ ] Implementation of Triple Persistence Manager.
- [ ] Generation of `builder_report.json`.

---

## 🏗️ Detailed Phase 02: Minimum Viable Product (MVP) - Endogenous Variables (PENDING)
**Objective:** Build a robust forecasting baseline using internal historical sales data and technical demand variables.

### Stage 2.1: Data Contract Validation (PENDING)
- [ ] Implementation of Quality Guardrail (MD5 Integrity, Watermarking).
- [ ] Development of `ContractValidator` with vectorized rules.
- [ ] Orchestration of `main.py` entrypoint.

### Stage 2.2: Data Loading & Health Dashboard (PENDING)
- [ ] Implementation of `DataLoader` with incremental logic.
- [ ] Development of Profiling Engine.
- [ ] Setup of Data Health Dashboard (Next.js).

### Other Stages (Abbreviated)
*   **Stage 2.3: Data Preprocessing (PENDING):** Target calculation (`demanda_teorica_total`).
*   **Stage 2.4: Exploratory Data Analysis (EDA) (PENDING):** Signal & Noise analysis.
*   **Stage 2.5: Feature Engineering (PENDING):** Creation of endogenous features (Lags, Rolling windows).
*   **Stage 2.6: Training and Modeling (PENDING):** Model benchmarking (`skforecast`).
*   **Stage 2.7: Invisibility & Inference (PENDING):** 95-day horizon forecasting.
*   **Stage 2.8: Dashboard Layout & Construction (PENDING):** Final MVP visualization.

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
*Last Edited: 2026-03-13*
