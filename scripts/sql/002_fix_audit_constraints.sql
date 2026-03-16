-- ==========================================================
-- SCRIPT: 002_fix_audit_constraints.sql
-- DESCRIPCIÓN: Corrección de restricción UNIQUE en semantic_hash
--              para permitir trazabilidad histórica de los mismos datos.
-- AUTOR: Antigravity AI
-- FECHA: 2026-03-15
-- ==========================================================

-- 1. Eliminar la restricción UNIQUE que bloquea el re-uso de estados de data
-- Buscamos el nombre de la restricción generado por PostgreSQL
ALTER TABLE public.sys_ingestion_audit 
DROP CONSTRAINT IF EXISTS sys_ingestion_audit_semantic_hash_key;

-- 2. Asegurar que exista un índice para búsquedas rápidas (por si se borró la restricción)
CREATE INDEX IF NOT EXISTS idx_audit_semantic_hash ON public.sys_ingestion_audit(semantic_hash);

-- 3. (Opcional) Agregar restricción de unicidad lógica para evitar duplicados en la misma ejecución
ALTER TABLE public.sys_ingestion_audit 
ADD CONSTRAINT sys_ingestion_audit_exec_table_unique UNIQUE (execution_id, table_name);

COMMENT ON CONSTRAINT sys_ingestion_audit_exec_table_unique ON public.sys_ingestion_audit 
IS 'Asegura que solo exista un reporte de auditoría por tabla en una misma ejecución del pipeline.';
