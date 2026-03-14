# [SPEC-F01-03] - Especificación Técnica: Contrato de Datos Manual
**ESTATUS:** 🟢 COMPLETADO

## 1. ARQUITECTURA LÓGICA (Technical Design)

El contrato de datos actúa como el **Middle-Layer** entre el conector de base de datos (`src/connector/`) y el motor de validación. Su función principal es desacoplar los nombres técnicos de Supabase de la lógica de negocio del modelo de forecasting.

### Flujo de Datos [ARC-03]
`Supabase (Postgres)` → `DBConnector` → `DataContract (YAML Definition)` → `DataLoader (Parquet Generation)`

---

## 2. ESTRUCTURA DEL CONTRATO (YAML Schema)

El archivo `contracts/contracts/data_contract.yaml` debe cumplir con el siguiente esquema estricto de validación:

### 2.1 Especificación de Campos por Fuente [ARC-DAT]
| Atributos | Tipo | Obligatorio | Propósito Técnico |
| :--- | :--- | :--- | :--- |
| `name` | String | Sí | Identificador único del dataset (Alias). Generará un archivo `[name].parquet`. |
| `db_table` | String | Sí | Nombre exacto de la tabla en Supabase configurada en `config.yaml`. |
| `primary_key` | String | Sí | Define la granularidad atómica y evita duplicación de registros. |
| `schema` | Map | Sí | Diccionario de tipos para casting estricto en el motor de procesamiento. |

### 2.2 Tipos de Datos y Mapeo Técnico
El contrato utiliza una nomenclatura simplificada que garantiza la compatibilidad entre el motor de base de datos y el motor de procesamiento (Pandas):

| Nomenclatura Contrato | Tipo Supabase (Postgres) | Tipo Pandas (Engine) |
| :--- | :--- | :--- |
| `datetime` | `date` / `timestamp` | `datetime64[ns]` |
| `int` | `integer` / `bigint` | `int64` |
| `float` | `numeric` / `double` | `float64` |
| `string` | `text` / `varchar` | `string` / `object` |
| `boolean` | `bool` | `bool` |

---

## 3. DISEÑO DE MAPEO (Mapping Logic)

El contrato debe permitir la abstracción total del origen. 

- **Abstracción de Archivo:** Aunque el dato venga de Supabase, el motor de forecasting lo consumirá internamente como un archivo con nombre `[name].parquet` (ej. `inventory.parquet`).
- **Validación de Identidad:** La clave `db_table` debe coincidir exactamente con el nombre de la tabla configurada en el conector de base de datos.

---

## 4. CASO DE USO: REGISTRO DE INVENTARIO (First Registration)

Para el arranque de esta etapa, se registrará la fuente `inventory` (mapeada a `usr_inventario_detallado`), la cual es crítica por contener la **variable target del proyecto**.

Para el arranque de esta etapa, se definirá la tabla `inventario_detallado`:

```yaml
data_sources:
  - name: "inventory"
    db_table: "usr_inventario_detallado"
    primary_key: "fecha"
    schema:
      fecha: "datetime"
      kit_inicial_bodega: "int"
      lbs_iniciales_bodega: "float"
      demanda_teorica_total: "int" # VARIABLE OBJETIVO
      # ... (total 17 columnas registradas)
  - name: "sales"
    db_table: "usr_ventas"
    # ...
  - name: "weather"
    db_table: "usr_clima_diario"
    # ...
```

---

## 5. MATRIZ DE DISEÑO VS PRD (Traceability)

| Especificación Téc. | Requerimiento PRD | Estado | Nota Técnica |
| :--- | :--- | :--- | :--- |
| `data_sources` structure | **[REQ-CTR-01]** | ✅ | Raíz única para escalabilidad |
| `name` to `.parquet` mapping | **[REQ-CTR-02]** | ✅ | Abstracción de archivo lógica |
| Pandas Type Dictionary | **[REQ-CTR-03]** | ✅ | Casting forzado en el pipeline |
| Inventory Definition | **[REQ-CTR-04]** | ✅ | 100% Alineada con DAT-03 |

---

## 6. CONTROL DE VERSIONES Y SEGURIDAD
- **Git State:** Versionado como código base (No DVC).
- **Inmutabilidad:** Una vez aceptado por un commit de Stage 1.3, cualquier cambio requiere un proceso de Gestión de Configuración.
- **Seguridad:** No se permiten URLs ni Keys dentro de este archivo.

---

## 7. CRITERIOS DE CALIDAD TÉCNICA
1.  **Validación de Sintaxis:** El archivo debe pasar cualquier linter de YAML estándar.
2.  **Integridad de Tipos:** Los tipos definidos en `schema` deben ser una de las palabras clave permitidas en la sección 2.3.
3.  **Unicidad de Nombres:** No pueden existir dos fuentes con el mismo `name`.

---
*Diseñado por Antigravity (Modo C: Tech Lead Architect) | 2026-03-14*
