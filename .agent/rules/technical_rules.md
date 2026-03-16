# [RULE-TECH] - Reglas Técnicas de Procesamiento y Modelado

## 1. Identificación y Control (Metadata)
*   **Título:** REGLAS TÉCNICAS (Technical Rules)
*   **Versión:** v1.1.0
*   **Estado:** Oficial / Aprobado
*   **Fecha de Creación:** 2026-03-13
*   **Trazabilidad:** Derivado de [Project_Charter.md](../../docs/artifacts/Project_Charter.md).
*   **Objetivo:** Establecer los estándares técnicos de procesamiento, modelado y validación para el ecosistema de pronóstico de **Bunuelos SAS** para el proyecto **Bunuelos_TuRedondito**.

---

## 2. Protocolo de Procesamiento de Datos (Data Engineering)

### 2.1 Upsampling y Alineación Temporal
*   **RT_DATA_001 (Upsampling Mensual):** Los datos con frecuencia mensual (ej. IPC, desempleo) deben propagarse a frecuencia diaria. Se utilizará el método de **propagación (Forward Fill)** desde el primer día del mes hasta el último.
*   **RT_DATA_002 (Upsampling Anual):** Los datos con frecuencia anual (ej. salario mínimo) se propagarán con valor constante desde el 1 de enero hasta el 31 de diciembre.
*   **RT_DATA_003 (Manejo de GAPs):** No se permiten huecos en las series una vez realizado el upsampling. Cualquier fecha faltante tras la alineación es un error crítico.

### 2.2 Ingeniería de Características (Features)
*   **RT_DATA_004 (Codificación Categórica):** Variables de texto (clima, festivos) deben convertirse en flags de 0/1 o One-Hot Encoding.
*   **RT_DATA_005 (Tratamiento COVID):** El periodo (01/05/2020 - 30/04/2021) debe marcarse con el flag `is_covid`.
*   **RT_DATA_006 (Variables de Marketing):** Variable flag para pauta iniciando 20 días antes de la promoción y terminando el día 25 del mes de finalización.

### 2.3 Gobernanza de Datos (DVC & Cloud-First)
*   **RT_DATA_007 (Versionamiento DVC):** Obligatorio versionar datasets crudos y transformados con DVC, utilizando **S3** como almacenamiento remoto.
*   **RT_DATA_008 (Snapshot de Entrenamiento):** Ejecutar `dvc commit` antes de cualquier entrenamiento para garantizar reproducibilidad.
*   **RT_DATA_009 (Integridad de Punteros):** Los archivos `.dvc` deben incluirse en el mismo commit de Git que el código asociado.
*   **RT_DATA_010 (Independencia Local):** El sistema no depende de archivos locales persistentes. Todo estado es restaurable desde Supabase o S3 via DVC.

---

## 3. Protocolo de Modelado (Machine Learning)

### 3.1 Arquitectura del Forecaster
*   **RT_ML_001 (Estrategia):** Uso mandatorio de `ForecasterAutoregDirect` (Multi-step).
*   **RT_ML_002 (Modelos):** Evaluación de Ridge, RandomForest, LightGBM, XGBoost, GradientBoosting e HistGradientBoosting.
*   **RT_ML_003 (Horizonte de Predicción):** Salida fija de **95 días**.

### 3.2 Entrenamiento y Backtesting
*   **RT_ML_004 (Ventana de Validación):** Estrategia de **Time Series Cross-Validation** (Rolling Window).
*   **RT_ML_005 (Métrica de Selección):** Éxito técnico definido por **MAPE < 15%**.
*   **RT_ML_006 (Overfitting):** Diferencia > 10% en MAPE entre train y test se considera sobreajuste.

---

## 4. Protocolo de Inferencia y Salida (Operational)

### 4.1 Regla de Oro de Inferencia
*   **RT_OPS_001 (Información Disponible):** Ejecución en día `X` solo utiliza datos validados hasta `X-1`. Prohibido el uso de información del día en curso.

### 4.2 Post-procesamiento y Cloud Sync
*   **RT_OPS_002 (Consolidación Mensual):** Resultados diarios sumados para generar meses completos.
*   **RT_OPS_003 (Truncamiento de Incertidumbre):** Descartar días de meses incompletos al final del horizonte de 95 días.
*   **RT_OPS_004 (Firma en Supabase):** Cada ejecución debe registrar su firma de estado y metadatos en Supabase para auditoría operativa.

---

## 5. Protocolo de Calidad y Monitoreo (MLOps)

### 5.1 Detección de Drift
*   **RT_MON_001 (Umbrales de Drift):** Z-Score de 2.0 y 3.0 para alertas. El Drift no bloquea la inferencia pero se registra.
*   **RT_MON_002 (Re-entrenamiento):** MAPE > 15% durante 2 semanas consecutivas dispara auditoría y re-entrenamiento forzado.

### 5.2 Gobernanza Evolutiva y Control de Cargas
*   **RT_GOV_001 (Gatekeeper Evolutivo):** El Gatekeeper debe permitir el ingreso de nuevas fuentes de datos declaradas en el contrato de manera automática. Solo se deben bloquear fuentes que tengan un fallo de certificación fallido registrado en la última ejecución de gobernanza.
*   **RT_GOV_002 (Modo Global Dinámico):** El modo de carga global (`load_type`) debe reportar el nivel máximo de actividad detectado: si alguna tabla secundaria carga datos (`FULL`), el proceso no puede marcarse como `NO_NEW_DATA`.
