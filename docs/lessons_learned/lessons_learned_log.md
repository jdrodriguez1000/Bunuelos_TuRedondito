# LOG DE LECCIONES APRENDIDAS - BUNUELOS_TUREDONDITO

Este documento registra los aprendizajes técnicos, de negocio y de proceso para garantizar la mejora continua del sistema de pronóstico de **Bunuelos SAS**.

---

| ID | Fecha | Fase | Categoría | Hecho / Hallazgo | Por Qué (Causa Raíz) | Acción Accionable |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| LL_001 | 2026-03-13 | 1.1 | PROCESS | Implementación de gobernanza robusta antes del código. | Evitar deriva técnica y falta de trazabilidad en proyectos previos de Forecasting. | Mantener el Mandato del Índice y SDD como pilares innegociables. |
| LL_002 | 2026-03-13 | 1.1 | TECHNICAL | Fallo de CI por carpetas vacías (src). | Git no trackea carpetas sin archivos por defecto, causando fallos en tests de estructura. | Usar `.gitkeep` en todas las carpetas base de la arquitectura (src, data, etc.). |
| LL_003 | 2026-03-13 | 1.1 | TECHNICAL | Integración de Release Please requiere PAT específico. | El token por defecto de GHA no tiene permisos suficientes para disparar otros workflows tras un squash merge. | Configurar `RELEASE_PLEASE_TOKEN` como Secret para habilitar releases automáticos. |
| LL_004 | 2026-03-13 | 1.1 | PROCESS | Restricción de autonomía del agente (Regla C1.4). | El usuario prefiere control total sobre el avance de archivos y fases para evitar cambios no supervisados. | Mantener las reglas C1.3 y C1.4 en `.clinerules` para forzar paradas de validación. |
| LL_005 | 2026-03-14 | 1.2 | TECHNICAL | Singleton Guard Pattern previene inundación de sockets. | Múltiples importaciones en pipelines asíncronos pueden saturar los pools de conexión de Supabase (Max 200 en planes base). | Implementar el Singleton en el método `__new__` con Lazy Loading de variables de entorno. |
| LL_006 | 2026-03-14 | 1.2 | ARCH | Dual-Access Client (Service Role) facilita la observabilidad. | Las políticas RLS restringen la escritura de logs técnicos si no hay un usuario autenticado. | Separar el `Anon Client` del `Service Client` permitiendo escritura de logs de sistema sin vulnerar RLS. |
| LL_007 | 2026-03-14 | 1.2 | PROCESS | Configuración Centralizada (Zero Hardcoding). | El código quemado dificulta la migración entre entornos y la trazabilidad de rutas. | Usar `config.yaml` como Única Fuente de Verdad para todas las rutas y parámetros técnicos. |
| LL_008 | 2026-03-14 | 1.2 | TECHNICAL | Doble Persistencia de Reportes (Latest/History). | Se perdía la trazabilidad histórica de los spikes de rendimiento al sobreescribir archivos. | Implementar guardado dual: archivo `latest` para consumo rápido y `history/` con timestamp para auditoría. |
| LL_009 | 2026-03-14 | 1.2 | ARCH | Configuración S3 mediante metadatos en YAML. | La conexión S3 requiere múltiples llaves que ensucian el código de inicialización. | Mapear nombres de variables de entorno en YAML para desacoplar la lógica del conector de los nombres físicos del `.env`. |
