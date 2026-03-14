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

| LL_010 | 2026-03-14 | 1.3 | TECHNICAL | Degradación de Tipos (Object casting) en APIs REST. | Supabase serializa fechas como String, causando que Pandas las detecte como `object`. | Parametrizar contratos como `datetime` y usar coerción forzada para validar integridad. |
| LL_011 | 2026-03-14 | 1.3 | PROCESS | Contratos de Datos Agnósticos (Gobernanza Pura). | Definir contratos ayuda a desacoplar la base de datos del pipeline, permitiendo fallos controlados. | El contrato debe describir cómo DEBE ser el dato, no cómo llega de la fuente. |
| LL_012 | 2026-03-14 | 1.3 | PROCESS | Suite de Validación Jerárquica [T-1.3-05]. | Modificar el contrato puede romper la sincronización con la configuración global (`config.yaml`). | Implementar pruebas que validen la alineación entre fuente mandatoria y target en el contrato. |
| LL_013 | 2026-03-14 | 1.3 | PROCESS | Sincronización Estricta de DDL SQL. | Columnas desactualizadas en el contrato causan fallos en las queries futuras. | Siempre sincronizar el `.yaml` contra el DDL oficial de Supabase antes de cerrar contratos. |

| LL_014 | 2026-03-14 | 2.1 | TECHNICAL | Detección de Deltas por Hash Semántico. | Evitar procesar datos idénticos ahorra costos de computación y previene duplicados en el modelo. | Implementar el `Semantic Fingerprint` basado en esquema, conteo y muestra de datos (BR-21-05). |
| LL_015 | 2026-03-14 | 2.1 | DATA | Perfilamiento Avanzado para Observabilidad. | Solo validar tipos no es suficiente para IA; detectar atípicos (outliers) previene sesgos en el Forecast. | Incluir Cuartiles, IQR y análisis de frecuencias categóricas en cada reporte de validación. |
| LL_016 | 2026-03-14 | 2.1 | ARCH | Blindaje "Día Cero" (Fail-Safe Architecture). | Si falla la configuración inicial, el sistema debe reportar el error antes de colapsar localmente. | Registrar `GOVERNMENT_ERROR` en Supabase incluso si no existe el archivo de contrato. |
| LL_017 | 2026-03-14 | 2.1 | PROCESS | Alineación Negocio-Carpeta (Stage Load). | Los nombres técnicos (`stage_validator`) pueden confundir al negocio sobre el negocio sobre el avance real del pipeline. | Renombrar etapas de salida basándose en procesos de negocio (Load, Train, Forecast) no en herramientas. |
