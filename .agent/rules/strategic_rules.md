# [RULE-STRAT] - Reglas Estratégicas y Alineación de Negocio

## 1. Identificación y Control (Metadata)
*   **Título del Documento:** REGLAS ESTRATÉGICAS (Strategic Rules)
*   **Versión:** v1.0.0
*   **Estado:** Oficial / Aprobado
*   **Fecha de Creación:** 2026-03-13
*   **Trazabilidad:** Derivado de [Project_Charter.md](../../docs/artifacts/Project_Charter.md).
*   **Objetivo:** Definir las directrices de alto nivel para la toma de decisiones, la adopción del sistema y la gestión de la neutralidad en el proceso de pronóstico de **Bunuelos SAS** para el proyecto **Bunuelos_TuRedondito**.

---

## 2. Principios de Neutralidad y Objetividad

### 2.1 Eliminación del Sesgo Humano
*   **RE_STRAT_001 (Prioridad del Dato):** El modelo debe ser alimentado exclusivamente con datos objetivos de la base de datos (Supabase). No se permite la inyección manual de "ajustes por presentimiento" antes del procesamiento del modelo.
*   **RE_STRAT_002 (Neutralidad de Pronóstico):** Ante una discrepancia entre la cifra histórica y la opinión subjetiva de un analista, el modelo debe priorizar la tendencia estadística, documentando la diferencia si es superior al 20%.
*   **RE_STRAT_003 (El Objetivo del 15%):** El éxito técnico se define por alcanzar y mantener un **MAPE inferior al 15%** en el set de validación. Cualquier modelo que no mejore el benchmark `Naive` no será considerado para producción.

---

## 3. Protocolo de Adopción y Comité de Expertos

### 3.1 El Rol del Panel de Expertos
*   **RE_STRAT_004 (Modelo como Referencia):** El pronóstico generado por **Triple S** será considerado el "Insumo Principal" y el **Ancla de Verdad** para las reuniones de planeación y compra de Kit en **Bunuelos SAS**.
*   **RE_STRAT_005 (Transparencia de Decisiones):** Si el comité decide modificar una cifra del pronóstico, debe registrarse el motivo y la magnitud del cambio en Supabase para realizar auditorías de "Bias" (sesgo) a futuro.

---

## 4. Gestión de Escenarios y Simulaciones

### 4.1 Toma de Decisiones "What-If"
*   **RE_STRAT_006 (Simulación Basada en Evidencia):** Las simulaciones (precios, 2x1, inflación) son herramientas de planificación estratégica, no promesas de venta garantizada.
*   **RE_STRAT_007 (Horizonte y Consistencia):** El pronóstico base será de **95 días**. Para el cliente se presentarán **3 meses naturales** (Actual + 2), truncando días residuales para evitar incertidumbre.

---

## 5. Mejora Continua y Gobernanza de IA

### 5.1 Evolución del Ecosistema
*   **RE_STRAT_008 (Auditabilidad y Drift):** Todo fallo técnico o desviación de MAPE > 15% debe ser revisado mensualmente. Se seguirá el plan evolutivo de 7 fases sin saltar etapas para garantizar la estabilidad.
*   **RE_STRAT_009 (Fuente Única de Verdad - SSOT):** La única fuente aceptada para entrenamiento es la data validada en **Supabase** y los artefactos en **S3/DVC**. Prohibido el uso de hojas de cálculo externas o informales.
