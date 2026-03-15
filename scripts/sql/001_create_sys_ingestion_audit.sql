-- ==========================================================
-- SCRIPT: 001_create_sys_ingestion_audit.sql
-- DESCRIPCIÓN: Creación de la tabla de auditoría para la 
--              Etapa 2.2 (Ingestión Bronce).
-- AUTOR: Antigravity AI
-- FECHA: 2026-03-15
-- ==========================================================

-- 1. Crear la tabla de auditoría
CREATE TABLE IF NOT EXISTS public.sys_ingestion_audit (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    execution_id UUID NOT NULL, -- FK a futuro para trazabilidad de pipeline
    table_name TEXT NOT NULL,
    semantic_hash TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL CHECK (status IN ('SUCCESS', 'FAILED', 'NO_DATA', 'WARNING')),
    health_score FLOAT NOT NULL CHECK (health_score >= 0 AND health_score <= 100),
    row_count INTEGER NOT NULL DEFAULT 0,
    health_report JSONB NOT NULL, -- Reporte detallado para el Dashboard (Next.js)
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 2. Habilitar Row Level Security (RLS)
ALTER TABLE public.sys_ingestion_audit ENABLE ROW LEVEL SECURITY;

-- 3. Definir Políticas de Seguridad (Supabase Best Practices)

-- 3.1 Política de Lectura: Solo usuarios autenticados (Dashboard)
CREATE POLICY "Allow authenticated reads" 
ON public.sys_ingestion_audit
FOR SELECT 
TO authenticated 
USING (true);

-- 3.2 Política de Inserción: Solo el service_role (Ingestor Python)
CREATE POLICY "Allow service_role insertion" 
ON public.sys_ingestion_audit
FOR INSERT 
TO service_role 
WITH CHECK (true);

-- 3.3 Política de Actualización: Solo el service_role (si aplica)
CREATE POLICY "Allow service_role updates" 
ON public.sys_ingestion_audit
FOR UPDATE 
TO service_role 
USING (true);

-- 4. Crear Índices para Optimización del Dashboard
CREATE INDEX IF NOT EXISTS idx_audit_table_name ON public.sys_ingestion_audit(table_name);
CREATE INDEX IF NOT EXISTS idx_audit_created_at ON public.sys_ingestion_audit(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_status ON public.sys_ingestion_audit(status);

-- 5. Comentario de Tabla
COMMENT ON TABLE public.sys_ingestion_audit IS 'Tabla de auditoría de salud de datos para la capa Bronce (Stage 2.2). Consumida por el Dashboard en Next.js.';
