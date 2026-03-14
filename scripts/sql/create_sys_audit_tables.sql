-- ------------------------------------------------------------------------------
-- PROYECTO: Bunuelos_TuRedondito
-- DESCRIPCIÓN: Creación de tablas de auditoría para el motor de validación.
-- ETAPA: 2.1 - Validation & Ingest Certification
-- ------------------------------------------------------------------------------

-- 1. Tabla: sys_validation_contract
-- Almacena el resultado de cada validación de contrato y perfilamiento.
CREATE TABLE IF NOT EXISTS public.sys_validation_contract (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contract_yaml TEXT NOT NULL,
    contract_hash TEXT NOT NULL,
    support_json JSONB NOT NULL,
    dvc_hash TEXT NOT NULL, -- Semantic Fingerprint
    s3_pointer_uri TEXT,    -- Link al ticket en S3
    total_tables INT NOT NULL DEFAULT 0,
    success_tables INT NOT NULL DEFAULT 0,
    failed_tables INT NOT NULL DEFAULT 0,
    status TEXT NOT NULL CHECK (status IN ('VALID', 'INVALID')),
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 2. Tabla: sys_pipeline_execution
-- Registra cada paso del orquestador main.py.
CREATE TABLE IF NOT EXISTS public.sys_pipeline_execution (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    process_name TEXT NOT NULL, -- 'validation', 'ingestion', etc.
    execution_mode TEXT NOT NULL, -- 'load', 'train', 'forecast'
    validation_id UUID REFERENCES public.sys_validation_contract(id),
    status TEXT NOT NULL DEFAULT 'RUNNING',
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- ------------------------------------------------------------------------------
-- 3. SEGURIDAD (Row Level Security - RLS)
-- Supabase es exigente: el service_role debe poder operar sin restricciones, 
-- pero bloqueamos acceso público.
-- ------------------------------------------------------------------------------

-- Habilitar RLS
ALTER TABLE public.sys_validation_contract ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.sys_pipeline_execution ENABLE ROW LEVEL SECURITY;

-- Política para sys_validation_contract
-- Permitir todo al service_role (Admin)
CREATE POLICY "Allow all for service_role on validation_contract" 
ON public.sys_validation_contract 
FOR ALL 
TO service_role 
USING (true) 
WITH CHECK (true);

-- Política para sys_pipeline_execution
-- Permitir todo al service_role (Admin)
CREATE POLICY "Allow all for service_role on pipeline_execution" 
ON public.sys_pipeline_execution 
FOR ALL 
TO service_role 
USING (true) 
WITH CHECK (true);

-- Notas para el usuario:
-- Ejecutar este script en el SQL Editor de Supabase.
-- Asegúrate de que las políticas permitan que el motor (usando service_role) pueda insertar registros.
