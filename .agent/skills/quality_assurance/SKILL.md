---
name: quality_assurance_expert
description: Especialista en la orquestación de pruebas automatizadas y gestión de reportes de salud técnica con doble persistencia.
---

# Skill: Experto en Calidad y QA

Esta habilidad habilita al agente para administrar el ciclo de vida del testing en **Bunuelos_TuRedondito**, asegurando que cada componente sea validado antes de su integración.

## 🛠️ 1. Capacidades Técnicas

### A. Orquestación jerárquica
- Ejecución inteligente de suites siguiendo el orden: `unit` -> `integration` -> `functional`.
- Implementación de lógica de aborto temprano (Fail-Fast).

### B. Generador de Reportes Granulares
- Capacidad para interceptar la salida de `pytest` y transformarla en el formato `tests_report.json` conforme a las [[RULE-QA]](../../rules/testing_rules.md).
- Inyección de metadatos de ejecución (timestamp, fase actual).

### C. Gestión de Doble Persistencia
- Automatización del archivado en `tests/reports/history/` tras cada ejecución.
- Mantenimiento del puntero `latest` para auditoría inmediata.

## 🛡️ 2. Protocolos de Seguridad
- **Validación de Entorno**: Verifica que el entorno virtual (`venv`) esté activo.
- **Protección de Credenciales**: Asegura que los reportes no contengan secretos o llaves de acceso sensibles.

## 📋 3. Formato del Reporte Estándar
```json
[
  {
    "type": "Unitaria",
    "status": "PASSED",
    "timestamp": "YYYY-MM-DDTHH:MM:SS",
    "details": "Resultados de la suite Unitaria",
    "tests": [
      {
        "name": "[test_file.py] test_function_name",
        "status": "PASSED"
      }
    ]
  }
]
```
