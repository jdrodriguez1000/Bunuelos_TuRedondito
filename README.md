# Proyecto de Forecasting: Bunuelos Tu Redondito

Este proyecto es desarrollado por **Sabbia Solutions & Services SAS (Triple S)** para el cliente **Bunuelos SAS**.

## 🚀 Objetivo
Desarrollar una aplicación de forecasting basada en datos históricos para predecir la demanda real del producto estrella (el buñuelo) con un horizonte de 6 meses, reduciendo el sesgo humano y los desfases actuales del 25%.

## 📂 Estructura del Proyecto
- `.agent/`: Reglas, habilidades y workflows del agente AI.
- `src/`: Código fuente del motor de forecasting y aplicación.
- `tests/`: Pruebas unitarias, integración y Quality Gate.
- `docs/`: Documentación del proyecto y Project Charter.
- `data/`: Datos crudos y procesados (gestionados por DVC).
- `scripts/`: Utilidades operativas y automatización.
- `notebooks/`: Experimentos y análisis de datos exploratorios.
- `outputs/`: Reportes generados y modelos entrenados.

## 🛠️ Tecnologías
*   **Python:** Procesamiento de datos y modelos estadísticos.
*   **Skforecast/Scikit-learn:** Modelado de forecasting.
*   **Supabase:** Base de datos relacional y persistencia.
*   **GitHub Actions:** CI/CD y Quality Gate.
*   **DVC:** Control de versiones de datos.

## 📊 Estado de Infraestructura
- [x] Repositorio GitHub Inicializado
- [x] Protección de Rama `main` Configurada
- [x] Secrets de Supabase Configurados
- [x] CI Quality Gate Validado

## 📄 Documentación Principal
*   [Project Charter](docs/artifacts/Project_Charter.md)
*   [Índice Maestro](index.md)

## 📜 Historial de Cambios (Log)
- **v0.1.0 (2026-03-13):** Inicialización de infraestructura, CI/CD y reglas de gobernanza.
