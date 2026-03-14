# [SPEC-F01-02] - Technical Specification: Database Connection (Stage 1.2)

Este documento define la arquitectura técnica y los estándares de implementación para la capa de persistencia de **Bunuelos_TuRedondito**, garantizando una conexión segura, eficiente y trazable hacia **Supabase Cloud**.

---

## 1. Arquitectura y Diagrama Lógico [ARC-07]

### Patrón Singleton y "Singleton Guard"
La clase `DBConnector` implementará el patrón **Singleton**. Actuará como un **Singleton Guard**, interceptando cualquier solicitud de instancia: si ya existe un cliente activo, lo retorna; de lo contrario, realiza la carga perezosa (lazy load) de las variables del entorno (`.env`) e inicializa la conexión.

```mermaid
graph TD
    subgraph Client_App ["Capa de Aplicación (src/)"]
        M1["extraer.py"]
        M2["validar.py"]
        M3["entrenar.py"]
    end

    subgraph Connector_Layer ["Capa de Conector (Singleton Guard)"]
        CB["DBConnector.__new__()"]
        LC{{"Check Instance"}}
        CONF["config.yaml (Source of Truth)"]
        ENV[".env Store (Contexto)"]
        SC["Standard Client (Anon)"]
        AC["Admin Client (Service Role)"]
        S3C["S3/DVC Client"]
    end

    subgraph Remote_Cloud ["Infraestructura Supabase"]
        S_URL["PostgREST API Endpoint"]
        S_DB["PostgreSQL DB"]
        S_S3["S3 Bucket (DVC)"]
    end

    M1 & M2 & M3 -->|get_instance()| CB
    CB --> LC
    LC -->|If None| CONF
    CONF --> ENV
    ENV -->|Init| SC & AC & S3C
    LC -->|If Exists| SC & AC & S3C
    SC & AC <==>|HTTPS (Batch Mode)| S_URL
    S3C <==>|Boto3 / DVC Protocol| S_S3
    S_URL <==> S_DB
```

---

## 2. Specs de Ingeniería de Datos (Data Pipeline) [DAT-01 a DAT-09]

### Protocolo y Formatos
*   **Protocolo:** Acceso vía HTTPS mediante la API REST (PostgREST) proporcionada por Supabase (SDK v2.x).
*   **Modo de Ingesta:** Batch (optimizado para la carga histórica inicial y actualizaciones diarias).
*   **Formatos de Salida:** El conector facilitará la exportación de resultados directamente en objetos serializables (**JSON**) o estructuras de alto rendimiento (**Pandas DataFrame**).

### Resiliencia y Tratamiento
*   **Manejo de Red:** Implementación de bloques `try-except` granulares para manejar inconsistencias de red, asegurando el cumplimiento de **[REQ-INF-02]**.
*   **Timeouts:** Configuración de 10 segundos para evitar bloqueos en el pipeline de CI/CD.

### Configuración de Almacenamiento S3 (DVC)
*   **Endpoint:** `SUPABASE_S3_ENDPOINT` (compatible con API S3).
*   **Bucket:** `dvc_Bunuelos_TuRedondito`.
*   **Propósito:** Los archivos pesados NO tocan el repositorio Git; se sincronizan directamente con este bucket mediante el protocolo S3.

---

## 3. Diseño del Modelo de Machine Learning (Data Science Connectivity)

Aunque esta fase es de infraestructura, sienta las bases para el motor predictivo:
*   **Extracción Selectiva:** La arquitectura permite la descarga de datos por granularidad (Diaria/Mensual) para alimentar el motor de `skforecast` en fases futuras.
*   **Métricas de Desempeño [MET-INF-01]:** Se habilita la recolección automática de métricas de latencia de conexión, impactando directamente en la eficiencia del entrenamiento futuro.

---

## 4. Especificaciones de Integración (Software Engineering)

### Anatomía de `src/connector/db_connector.py`
El conector implementará los siguientes métodos clave para cumplir con **[REQ-CON-01]**, **[REQ-SEC-01]** y **[REQ-ARC-01]**:

| Método | Descripción / Requerimiento Trazado |
| :--- | :--- |
| `_initialize_clients()` | Inyecta `SUPABASE_URL` y `SUPABASE_KEY` desde el contexto de memoria. |
| `get_client()` | Retorna el cliente estándar (Anon para RLS). |
| `get_service_client()` | Retorna el cliente administrativo para bypass de RLS (`SUPABASE_SERVICE_ROLE_KEY`). |
| `test_connection()` | Ejecuta un `SELECT count` sobre la tabla `usr_ventas` (**[DAT-01]**) para verificar salud y visibilidad. |

---

## 5. MLOps, Infraestructura y Despliegue

### Gobernanza y Cómputo
*   **Gestión de Secretos:** Los secretos nunca deben tocar el sistema de archivos de producción de forma plana; se gestionan exclusivamente en el entorno de ejecución (memoria).
*   **Parametrización [D3.2]:** Todas las rutas de archivos, nombres de bucket y tablas se cargan desde `config.yaml`.
*   **Doble Persistencia de Reportes [RULE-QA]:** 
    - El reporte de salida será `connector_report.json`.
    - Ubicación: `outputs/reports/stage_connector/`.
    - Se guardará una copia `latest` y una copia histórica con timestamp en la carpeta `history/`.
*   **Handshake Latency [MET-INF-01]:** El tiempo de respuesta de `test_connection()` debe ser inferior a 2 segundos en el pipeline de integracion.

---

## 6. Matriz de Diseño Técnico vs. PRD

| Componente Técnico | Historia de Usuario / REQ | Etiquetas Vinculadas |
| :--- | :--- | :--- |
| **Singleton Guard en `DBConnector`** | Centralización de accesos | **[REQ-CON-01]**, **[ARC-07]** |
| **Inyección via Load_Dotenv** | Gestión de Secretos en Memoria | **[REQ-SEC-01]**, **[MET-INF-02]** |
| **Dual-Client Proxy (Std/Admin)** | Soporte administrativo y RLS | **[REQ-ARC-01]**, **[REQ-INF-03]** |
| **Metodo `test_connection()`** | Validación de salud con `usr_ventas` | **[REQ-VAL-01]**, **[DAT-01]** |
| **Métricas de Latencia (<2s)** | Eficiencia en el Pipeline | **[MET-INF-01]** |

---
> [!IMPORTANT]
> **Definición de Salida:** Las consultas deben retornar objetos optimizados para su transformación inmediata a tipos de datos nativos de Python/Pandas para evitar cuellos de botella en la deserialización.

*Refinado por Antigravity (Modo C: Tech Lead Architect) | 2026-03-14*
