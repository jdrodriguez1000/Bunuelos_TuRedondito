# Project Charter: Forecasting de Demanda de Buñuelos

| Información del Proyecto | Detalle |
| :--- | :--- |
| **Nombre del Proyecto** | Sistema de Predicción de Demanda "Tu Redondito" |
| **Cliente** | Bunuelos SAS |
| **Consultor / Ejecutor** | Sabbia Solutions & Services SAS (Triple S) |
| **Fecha de Creación** | 13 de Marzo de 2026 |
| **Estado** | Borrador Inicial |

---

## 1. Propósito y Justificación del Proyecto
Bunuelos SAS enfrenta desafíos críticos en la gestión de su inventario debido a la inexactitud en los pronósticos de demanda de su producto estrella: el buñuelo. Actualmente, el proceso depende de un comité de expertos con criterios inconsistentes y alta influencia jerárquica, lo que resulta en:
*   **Desfases de hasta el 25%** entre lo planeado y lo real.
*   **Quiebres de stock** (pérdida de ventas).
*   **Excesos de inventario** (sobrecostos de producción y almacenamiento).

El proyecto busca implementar una solución técnica basada en datos que estandarice el criterio de pronóstico, reduzca el sesgo humano y mejore la precisión operativa.

## 2. Objetivos del Proyecto (S.M.A.R.T.)
1.  **Precisión:** Reducir el margen de error del pronóstico (actualmente 25%) a un rango significativamente menor (objetivo preliminar: <10-15%) utilizando modelos estadísticos/ML.
2.  **Horizonte:** Generar proyecciones automáticas con una ventana de **3 meses** a futuro.
3.  **Objetividad:** Eliminar la subjetividad y la influencia política en la generación de la cifra base de demanda.
4.  **Eficiencia:** Automatizar la agrupación y análisis de datos diarios para generar pronósticos confiables.

## 3. Filosofía de Desarrollo
El proyecto se rige por los principios de:
*   **"Menos es Más":** Simplicidad en la arquitectura para garantizar mantenibilidad.
*   **"Producción Primero":** Enfoque en generar resultados tangibles desde las etapas tempranas.
*   **Desarrollo por Capas:** El modelo y la herramienta crecerán de forma iterativa y modular, agregando complejidad solo cuando se demuestre que genera valor real a los resultados.

## 4. Hoja de Ruta (Roadmap) y Fases
El desarrollo se estructurará en 6 fases incrementales:

### Phase 1: Kickoff and Implementation
1. Infraestructura y documentación inicial.
2. Conexión a base de datos (Supabase).
3. Configuración del contrato de datos.

### Phase 2: Minimum Viable Product (MVP) - Endogenous Variables
*Basado en datos históricos de ventas y series temporales puras.*
1. Validación de contrato.
2. Carga de datos.
3. Preprocesamiento.
4. Análisis Exploratorio de Datos (EDA).
5. Ingeniería de características.
6. Entrenamiento y modelado.
7. Inferencias.
8. Dashboard (Versión Inicial).

### Phase 3: Robustness - Calendar
Agregación de variables exógenas asociadas al calendario (Feriados, Fines de semana, Quincenas) para robustecer el MVP.

### Phase 4: Controllable Variables - Commercial & Marketing
Integración de datos controlables por el cliente: Publicidad, Promociones (2x1) y Marketing Digital.

### Phase 5: External Non-Controllable Variables - Macro & Weather
Integración de factores externos: Clima (Lluvias) y variables macroeconómicas (IPC, TRM, Desempleo, Salario Mínimo).

### Phase 6: "Black Swan" Events
Modelado de efectos extremos y atípicos como la pandemia (COVID-19) para mejorar la resiliencia del modelo ante anomalías futuras.

*Nota: El dashboard evolucionará en funcionalidades y profundidad visual a medida que se avance en cada fase.*

## 5. Especificaciones Técnicas del Modelo
Para garantizar la robustez y precisión técnica de **Triple S**, se definen los siguientes parámetros de modelado:
*   **Librería Principal:** [skforecast](https://joaquinamatrodrigo.github.io/skforecast/).
*   **Estrategia de Forecasting:** Forecaster **Direct** (Direct Multi-step Forecasting).
*   **Algoritmos a Evaluar:** Ridge, Random Forest, LightGBM, XGBoost, Gradient Boosting, HistGradient Boosting.
*   **Variable Objetivo:** `demanda_teorica_total` (de la tabla `usr_inventario_detallado`).
*   **Granularidad y Horizonte:**
    *   **Entrenamiento y Predicción:** Diaria.
    *   **Horizonte de Ventas:** **95 días** continuos.
    *   **Regla de Oro (Lag T-1):** El modelo no considerará el día actual (Día X) para evitar sesgos por datos incompletos. Se basará siempre en información cerrada hasta el día anterior (X-1).
*   **Agregación y Presentación:**
    *   Los resultados diarios se agruparán mensualmente para la entrega al cliente.
    *   **Lógica de Visualización:** Se mostrará el mes actual + 2 meses siguientes (Horizonte de 3 meses). Los días excedentes del cuarto mes se eliminarán para asegurar que solo se presenten periodos mensuales completos y evitar incertidumbre.

## 6. Alcance del Proyecto
### Incluido:
*   Análisis de datos históricos diarios y modelado de estacionalidades complejas.
*   Desarrollo de un motor de forecasting que capture efectos de quincenas, ferias y festividades.
*   **Módulo de Simulaciones "What-If":** Capacidad de proyectar escenarios basados en cambios de variables críticas (Precio, Promociones, Macroeconomía y Clima).
*   Limpieza y tratamiento de anomalías históricas (incluyendo el periodo atípico de COVID-19).
*   Dashboard de visualización para la toma de decisiones gerenciales e iteración de escenarios.
*   Generación de reportes de pronóstico para los próximos 3 meses.

### Excluido:
*   Gestión de inventarios en tiempo real o logística de última milla.
*   Pronóstico de productos secundarios no definidos como "estrella".

## 7. Escenarios de Simulación (Análisis "What-If")
El sistema permitirá a la gerencia de Bunuelos SAS evaluar el impacto de decisiones estratégicas y factores externos mediante simulaciones:
*   **Sensibilidad de Precio:** ¿Qué sucede con la demanda si el precio unitario aumenta o disminuye en un X%?
*   **Optimización de Promociones:** Impacto de extender o reducir las ventanas de promoción (ej. +/- 5 o 10 días) sobre el agotamiento de stock y la merma.
*   **Escenarios Macroeconómicos:**
    *   Comportamiento de la demanda ante una inflación sostenida al alza.
    *   Relación Salario Mínimo vs Inflación (crecimiento por encima o por debajo del IPC).
*   **Escenarios Climáticos:** Impacto proyectado ante una semana de lluvias intensas persistentes.

## 8. Requerimientos de Negocio y Estacionalidad
El modelo deberá capturar las siguientes dinámicas identificadas por el negocio:
*   **Patrones Semanales:** Domingos (ventas pico), Sábados y Viernes. 
*   **Festivos:** Comportamiento similar a un sábado comercial.
*   **Efecto Quincena:** Incremento de ventas los días 15, 16, 30 y 31.
*   **Hitos Financieros (Prima):** Aumento de demanda entre el 15-20 de junio y 15-20 de diciembre.
*   **Eventos Especiales (Nivel Domingo):**
    *   Novenas Navideñas (16 al 26 de diciembre).
    *   Semana Santa (Jueves y Viernes Santo).
    *   Feria de las Flores (1 al 10 de agosto).
*   **Temporalidad Mensual:** Diciembre (mes líder), seguido de Enero, Junio y Julio.

## 9. Estrategia de Promociones y Marketing (Desde 2022)
El modelo debe considerar el impacto de las campañas promocionales estacionales:
*   **Mecánica de Promoción:** 2x1 (Paga 1, lleva 2).
*   **Ventanas de Promoción:**
    *   *Temporada 1:* 1 de Abril al 31 de Mayo.
    *   *Temporada 2:* 1 de Septiembre al 31 de Octubre.
*   **Estrategia de Pauta Digital (Facebook/Instagram Ads):**
    *   **Activación:** Inicia aproximadamente 20 días antes del comienzo de cada promoción.
    *   **Desactivación (Apagado):** Se realiza el día 25 del mes de cierre de la promoción (25 de mayo y 25 de octubre respectivamente).
*   **Impacto esperado:** El sistema debe correlacionar la inversión en `usr_marketing_digital` con el incremento en `unidades_bonificadas` y `unidades_totales` en la tabla de ventas.

## 10. Consideraciones de Datos Históricos
Para un entrenamiento robusto del modelo, se debe tener en cuenta la siguiente línea de tiempo de ventas:
*   **Anomalía COVID-19:** Del 1 de mayo de 2020 al 31 de abril de 2021 (Ventas significativamente bajas). Se requiere tratamiento de outliers o variables exógenas para evitar sesgos por este periodo.
*   **Periodo de Recuperación:** A partir de mayo de 2021.
*   **Nivel de Estabilidad (Baseline):** Del 2023 en adelante, las ventas se consideran en niveles normales/aceptables.

## 11. Operaciones y Logística de Inventario
El sistema deberá integrar las siguientes reglas de negocio para que el pronóstico sea accionable:
*   **Gestión de Materia Prima (Kit):**
    *   **Composición:** Mezcla de harina, queso, huevos, etc.
    *   **Conversión:** **1 lb de kit = 50 buñuelos**.
    *   **Ciclos de Pedido (Quincenales):**
        *   *Ciclo 1:* Pedido el día 15 para entrega a fin de mes (cubre del 1 al 14 del mes siguiente).
        *   *Ciclo 2:* Pedido el día 1 para entrega el día 14 (cubre del 15 al fin de mes).
    *   **Almacenamiento:** El kit en bodega es acumulable y no perenne en el corto plazo.
*   **Gestión de Producto Terminado (Buñuelo Frito):**
    *   **Perecedero:** Vida útil de **1 día**. No se puede reutilizar al día siguiente.
    *   **Desperdicio (Merma):** Buñuelos fritos no vendidos al cierre (pérdida total).
    *   **Costo de Oportunidad (Agotados):** Venta perdida por falta de producto preparado, incluso si hay materia prima en bodega.

## 12. Variables Externas e Hipótesis de Influencia
El proyecto evaluará la correlación e impacto de las siguientes variables externas en la demanda:
*   **Clima:** 
    *   *Hipótesis A:* Lluvia ligera incrementa las ventas (efecto "antojo").
    *   *Hipótesis B:* Lluvia fuerte disminuye las ventas (restricción de movilidad del cliente).
*   **Factores Macroeconómicos:** Se analizará la influencia de variables como:
    *   Alza en el Salario Mínimo (impacto en poder adquisitivo).
    *   TRM (Tasa Representativa del Mercado) - Impacto potencial en costos de insumos.
    *   IPC (Índice de Precios al Consumidor) - Inflación.
    *   Nivel de Desempleo.
    *   *Nota:* Aunque el cliente no tiene evidencia empírica, el sistema buscará identificar si estas variables tienen un peso estadístico relevante.

## 13. Infraestructura de Datos y Fuentes
El proyecto utiliza una infraestructura en la nube (**Supabase**) con datos históricos desde **Enero de 2017**. El sistema se actualiza automáticamente todos los días a las **1:00 AM (COT)**.

### Tablas y Frecuencias:
| Frecuencia | Nombre de Tabla | Descripción / Variables Clave |
| :--- | :--- | :--- |
| **Diaria** | `usr_clima_diario` | Precipitación, temperatura, eventos macro. |
| **Diaria** | `usr_ventas` | Unidades totales, pagas, bonificadas, promociones. |
| **Diaria** | `usr_inventario_detallado` | Kit en bodega, lbs, preparación, merma, agotados. |
| **Diaria** | `usr_finanzas_pyme` | Precios, costos y márgenes unitarios. |
| **Diaria** | `usr_trm_diaria` | Tasa Representativa del Mercado. |
| **Diaria** | `usr_marketing_digital` | Inversión en Ads (FB/IG), campañas activas. |
| **Mensual** | `usr_ipc_mensual` | Inflación mensual. |
| **Mensual** | `usr_desempleo_mensual` | Tasa de desempleo. |
| **Anual** | `usr_salario_minimo_anual` | Salario Mínimo Legal Vigente (SMLV). |

## 14. Stakeholders Clave
*   **Patrocinador (Cliente):** Gerencia General de Bunuelos SAS.
*   **Usuarios Clave:** Comités de Producción, Ventas y Finanzas.
*   **Equipo Técnico:** Sabbia Solutions & Services SAS (Triple S).

## 15. Riesgos Identificados
*   **Calidad de Datos:** Consistencia de la data diaria para capturar efectos de corta duración.
*   **Sesgo Histórico:** Que el periodo de pandemia distorsione el aprendizaje del modelo si no se trata adecuadamente.
*   **Resistencia al Cambio:** Influencia de gerentes que intenten ajustar el modelo sin base técnica.

## 16. Criterios de Éxito
El proyecto se considerará exitoso si se cumplen los siguientes hitos:
1.  **Excelencia Técnica:** El modelo seleccionado supera consistentemente a otros modelos evaluados en las métricas de error: **MAE**, **RMSE** y especialmente **MAPE** (Mean Absolute Percentage Error) en el set de validación.
2.  **Umbral de Precisión:** Se logra y mantiene una métrica **MAPE inferior al 15%**.
3.  **Adopción Organizacional:** La herramienta es oficialmente adoptada por el comité de expertos (Producción, Ventas y Finanzas) como el **insumo principal y base técnica** para sus proyecciones periódicas.
4.  **Reducción de Sesgo:** Disminución medible en el desfase entre lo planeado por el comité y la demanda real (comparado con el 25% histórico).

---
**Firmas de Aceptación:**

| Por Bunuelos SAS (Cliente) | Por Sabbia Solutions & Services SAS (Triple S) |
| :--- | :--- |
| __________________________ | __________________________ |
| Fecha: | Fecha: |
