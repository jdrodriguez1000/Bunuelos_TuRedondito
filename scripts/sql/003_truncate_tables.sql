-- 1. Limpieza de Auditoría de Ingesta (Borra el histórico de filas y salud)
TRUNCATE TABLE public.sys_ingestion_audit RESTART IDENTITY CASCADE;

-- 2. Limpieza de Ejecuciones del Pipeline (Borra el historial de corridas)
TRUNCATE TABLE public.sys_pipeline_execution RESTART IDENTITY CASCADE;

-- 3. Limpieza de Contratos de Datos (Activa el MODO HITO 0 / BOOTSTRAP)
TRUNCATE TABLE public.sys_validation_contract RESTART IDENTITY CASCADE;
