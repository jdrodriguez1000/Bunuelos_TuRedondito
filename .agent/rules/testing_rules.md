# [RULE-QA] - REGLAS DE TESTING Y CALIDAD

## 1. Identificación y Control (Metadata)
*   **Título:** Reglas de Testing y Aseguramiento de Calidad
*   **Versión:** v1.2.0
*   **Estado:** Oficial / Aprobado
*   **Trazabilidad:** Alineado con el Project Charter de **Bunuelos_TuRedondito**.
*   **Objetivo:** Garantizar la integridad del código y la exactitud de los pronósticos mediante validaciones jerárquicas.

---

## 🛡️ 2. Inmutabilidad y Aislamiento
- **Aislamiento Total (Unit)**: Las pruebas en `tests/unit/` deben ser 100% offline. Uso obligatorio de **Mocks** para cualquier dependencia externa (API, DB, S3).
- **Protección de Producción**: Queda prohibida la alteración de datos reales. Las pruebas de integración deben usar un esquema de Sandbox o realizar operaciones de solo lectura verificables.

## 🏗️ 3. Estructura y Jerarquía
- **Directorio Raíz**: `tests/`
- **Subcarpetas Obligatorias**:
    - `unit/`: Lógica pura, transformaciones y cálculos métricos (MAPE, MSE).
    - `integration/`: Validación de conectores (Supabase, S3) y carga de variables de entorno.
    - `functional/`: Flujos E2E de forecasting y generación de proyecciones oficiales.
    - `data/`: Pruebas de integridad de datasets versionados por DVC.
    - `reports/`: Almacenamiento de resultados y auditoría técnica.
- **Fail-Fast**: Si falla una prueba unitaria, la suite de integración y funcional **NO** se ejecuta.
- **Integridad DVC**: En etapas que involucren datasets, es MANDATORIO verificar que `dvc status` no reporte discrepancias antes de ejecutar las pruebas funcionales.

## 🧪 4. Estándares de Implementación
- **Framework**: Uso mandatorio de `pytest`.
- **Naming**: 
    - Archivos: `test_*.py`.
    - Funciones/Métodos: `test_[nombre_descriptivo]`.
- **Patrón AAA**: Estructura **Arrange** (Preparar), **Act** (Ejecutar), **Assert** (Validar).

## 📊 5. Protocolo de Reportes (Doble Persistencia)
- **Reporte Maestro**: `tests/reports/tests_report.json`.
- **Doble Persistencia**:
    - **Latest**: Se mantiene actualizado en la raíz de `reports/`.
    - **Histórico**: Copia con timestamp en `tests/reports/history/tests_report_YYYYMMDD_HHMMSS.json`.
- **Contenido Requerido**:
    - Metadatos (Fecha, Fase, Agente).
    - Detalle por prueba (Nombre, Estado, Mensaje de Error).
