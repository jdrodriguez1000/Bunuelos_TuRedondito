# LOG DE LECCIONES APRENDIDAS - BUNUELOS_TUREDONDITO

Este documento registra los aprendizajes técnicos, de negocio y de proceso para garantizar la mejora continua del sistema de pronóstico de **Bunuelos SAS**.

---

| ID | Fecha | Fase | Categoría | Hecho / Hallazgo | Por Qué (Causa Raíz) | Acción Accionable |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| LL_001 | 2026-03-13 | 1.1 | PROCESS | Implementación de gobernanza robusta antes del código. | Evitar deriva técnica y falta de trazabilidad en proyectos previos de Forecasting. | Mantener el Mandato del Índice y SDD como pilares innegociables. |
| LL_002 | 2026-03-13 | 1.1 | TECHNICAL | Fallo de CI por carpetas vacías (src). | Git no trackea carpetas sin archivos por defecto, causando fallos en tests de estructura. | Usar `.gitkeep` en todas las carpetas base de la arquitectura (src, data, etc.). |
| LL_003 | 2026-03-13 | 1.1 | TECHNICAL | Integración de Release Please requiere PAT específico. | El token por defecto de GHA no tiene permisos suficientes para disparar otros workflows tras un squash merge. | Configurar `RELEASE_PLEASE_TOKEN` como Secret para habilitar releases automáticos. |
| LL_004 | 2026-03-13 | 1.1 | PROCESS | Restricción de autonomía del agente (Regla C1.4). | El usuario prefiere control total sobre el avance de archivos y fases para evitar cambios no supervisados. | Mantener las reglas C1.3 y C1.4 en `.clinerules` para forzar paradas de validación. |
