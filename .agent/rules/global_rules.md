# [RULE-GLOBAL] - Protocolo de Gobernanza y Mandato Crítico

Estas reglas aplican dogmáticamente a **TODOS** los módulos, agentes, habilidades y scripts del proyecto **Bunuelos_TuRedondito**. Ninguna regla local puede sobreescribir u omitir estas directrices fundacionales.

---

## 1. Mantenimiento del Contexto y Eficiencia del Agente
- **C1.0 (Mandato del Índice):** Es OBLIGATORIO que la primera acción del agente en cada sesión sea leer el archivo `file:///c:/Users/USUARIO/Documents/Forecaster/Bunuelos_TuRedondito/index.md`. No se permite ninguna acción técnica sin haber validado el estado actual de la fase en el índice. El incumplimiento de esta regla invalida cualquier propuesta posterior.
- **C1.1 (Carga Selectiva):** No cargues jamás todas las especificaciones de forma indiscriminada. Una vez leído el índice, carga en memoria únicamente los archivos específicos del módulo, fase o etapa en el que vas a trabajar.
- **C1.2 (Evitar Ruido):** Si estás trabajando en un módulo específico (ej. "Data Contract"), ignora reglas o lógica de otros módulos (ej. "ML Training") a menos que haya una dependencia explícita.
- **C1.3 (Autorización Explícita de Archivos):** NUNCA escribas un documento o generes un archivo (commit a disco) sin que el usuario lo pida explícitamente. La proactividad debe limitarse a propuestas en el chat.
- **C1.4 (Mandato de No-Avance):** Queda terminantemente prohibido avanzar autónomamente a una nueva fase, etapa o archivo del proyecto sin que el usuario lo indique. El agente debe esperar la orden "Procede", "Siguiente" o similar antes de tocar un nuevo archivo.

## 2. Seguridad y Credenciales (Golden Rule)
- **S2.1 (Hardcoding Nulo):** ESTRICTAMENTE PROHIBIDO empotrar/hardcodear cadenas de conexión a base de datos, contraseñas, URLs de APIs, tokens o cualquier credencial en código `.py`, `.json` o `.yaml`.
- **S2.2 (Patrón .env):** Toda credencial secreta se consume exclusivamente mediante variables de entorno y archivos `.env` (no trackeados en Git).
- **S2.3 (Consistencia Temporal - DB Time):** Se prohíbe el uso de `datetime.now()` local. Toda referencia temporal operativa para filtros, watermarks o logs debe obtenerse de Supabase (`SELECT NOW()`) para evitar desincronías.

## 3. Filosofía "Spec-Driven Development" (SDD) y Cloud-First
- **D3.1 (Acatamiento de Documentos):** El código debe ser un reflejo exacto y sumiso a los documentos de `docs/specs/` y `.agent/rules/`.
- **D3.2 (Cero Hardcoding Lógico):** Prohibido hardcodear nombres de columnas, tablas o rutas locales. La única fuente de parametrización es el archivo `config.yaml`.
- **D3.3 (Independencia de Archivos Locales):** El proyecto no debe depender de persistencia local persistente. Los artefactos (modelos, reportes, datos transformados) deben residir en **Supabase** (logs/metadatos) y **S3** (mediante **DVC** para archivos pesados). La persistencia local es efímera y solo para procesamiento.
- **D3.4 (Triple Persistencia de Estado):** Cada fase debe registrar su éxito/fallo en:
    1.  Archivo local `latest` (para ejecución inmediata).
    2.  Archivo local con timestamp (para backup local).
    3.  **Firma de estado en Supabase** (Mandatorio para trazabilidad y salud del pipeline).
- **D3.5 (Sincronización Mandatoria):** Ante cualquier cambio lógico no documentado, **DETÉN LA IMPLEMENTACIÓN**. Actualiza el PRD/Spec primero, obtén aprobación y luego programa.

## 4. Ingeniería de Software de Alta Calidad
- **Q4.0 (Entorno Hermético):** Uso obligatorio de `venv` con Python 3.12+. Actualización inmediata de `requirements.txt`.
- **Q4.1 (Pushdown y Rendimiento):** Privilegia la ejecución de operaciones en la base de datos (SQL Pushdown / Supabase) en lugar de procesar grandes DataFrames en memoria local si no es estrictamente necesario.
- **Q4.2 (Gobernanza con DVC):** Obligatorio versionar artefactos (>1MB) con DVC. El comando `dvc push` al almacenamiento configurado (S3) es parte del flujo de entrega.
- **Q4.3 (Control de Excepciones):** Prohibido el uso de `pass` en excepciones. Todo error debe ser mapeado a códigos legibles (ej. `ERR_DB_001`) y registrado en Supabase.

## 5. Idioma y Nomenclatura
- **Nombres de Archivos y Carpetas**: Siempre en **Inglés** (ej. `data_loader.py`).
- **Contenido de Archivos**: Documentación, comentarios y explicaciones en **Español**.
- **Variables y Código**: Inglés (estándar), pero mensajes de salida al usuario en Español.
