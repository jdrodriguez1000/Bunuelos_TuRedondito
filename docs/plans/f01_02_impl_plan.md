# [IMPL-F01-02] - Implementation Plan: Database Connection (Stage 1.2)

Este documento detalla la hoja de ruta táctica para ejecutar la construcción del conector de base de datos de **Bunuelos_TuRedondito**, alineado con el **[SPEC-F01-02]** y los estándares de gobernanza ágil.

---

## 1. RESUMEN DEL CRONOGRAMA Y EQUIPO (Timeline & Resources)
*   **Sprint Asociado:** Sprint 1: Conectividad y Blindaje.
*   **Duración Estimada:** 1 Sesión (Foco en Calidad Atómica).
*   **Roles Ejecutores:**
    *   **Data Engineer (AI/Antigravity):** Implementación del conector y lógica de Singleton.
    *   **QA Analyst (AI/Antigravity):** Diseño y ejecución de Unit & Integration Tests.
    *   **Product Owner (User):** Validación de trazabilidad con el Charter.

---

## 2. RUTA CRÍTICA Y DEPENDENCIAS (Critical Path)
*   **Bloqueador Principal:** La visibilidad y permisos de las tablas core en Supabase **[DAT-01]** a **[DAT-06]**.
*   **Dependencia:** La implementación del "Data Contract" (Stage 1.3) no puede iniciar hasta que la conexión universal sea declarada estable y segura con soporte S3.
*   **Acción Paralela:** El QA puede empezar a escribir los Mocks de las tablas mientras el Data Engineer configura el cliente dual y el bucket S3 en DVC.

---

## 3. PRODUCT BACKLOG Y WBS (Work Breakdown Structure)

### Épica: Gobernanza de Datos e Infraestructura [EP-01]
| ID | Tarea | Descripción | Responsable | Etiqueta |
| :--- | :--- | :--- | :--- | :--- |
| **T-1.2-01** | Setup del Entorno Seguro | Configuración de `.env` y validación de `.gitignore`. | Data Engineer | **[REQ-SEC-01]** |
| **[T-1.2-02]** | Singleton Guard Implementation | Desarrollo de `db_connector.py` con lazy loading de `.env` y `config.yaml`. | Data Engineer | **[REQ-CON-01]**, **[ARC-07]** |
| **[T-1.2-03]** | Dual-Client Proxy & S3 Config | Configuración de clientes Anon/Service y parámetros S3. | Data Engineer | **[REQ-ARC-01]** |
| **[T-1.2-04]** | Performance Spike | Prueba de latencia (<2s) y reporte `connector_report.json` con doble persistencia. | Data Engineer | **[MET-INF-01]** |
| **T-1.2-05** | Suite de Pruebas Core | Implementación de tests unitarios e integración real. | QA Analyst | **[REQ-VAL-01]** |

---

## 4. PLANIFICACIÓN POR SPRINTS (Sprint Roadmap)

### Sprint 1: Conectividad y Blindaje (Current)
*   **Objetivo del Sprint:** Lograr una conexión 100% estable, segura e invisible para el resto de la aplicación, con reporte de calidad generado.
*   **Entregables Críticos:**
    *   `src/connector/db_connector.py` operativo.
    *   `tests/reports/latest/tests_report.json` con 100% de éxito.
    *   Acceso verificado a los datos diarios de ventas (**[DAT-01]**).

---

## 5. PLAN DE PRUEBAS Y UAT (Quality Assurance)

### Pruebas Técnicas
*   **Unitarias:** Validar que `DBConnector()` retorne siempre la misma instancia de memoria (Id Check).
*   **Seguridad:** Confirmar que el uso del `Service Role` sea auditado y lance excepción si la llave falta en `.env`.
*   **Integración:** Ejecución de `test_connection()` contra la tabla real `usr_ventas`.

### UAT (Aceptación de Negocio)
*   **Demostración:** Lectura exitosa de un registro de ventas histórico sin exposición de credenciales en pantalla o logs públicos.

---

## 6. RITOS ÁGILES Y GOBERNANZA

### Definition of Done (DoD) de la Fase
*   Código en `src/` modular, documentado y siguiendo el patrón Singleton.
*   Pruebas en `tests/` con paso exitoso (100% Green).
*   Reporte consolidado con **doble persistencia** (Latest y Archive con timestamp).
*   Trazabilidad total de métricas **[MET-INF-01]** (Latencia) y **[MET-INF-02]** (Seguridad).

---
> [!IMPORTANT]
> **Riesgo Identificado [RSK-04]:** El bypass de RLS mediante el Service Role podría ser mal utilizado.
> **Mitigación:** El método `get_service_client()` debe estar explícitamente desacoplado de los flujos de extracción de datos del MVP.

*Plan refinado por Antigravity (Modo D: Orquestador de Entrega) | 2026-03-14*
