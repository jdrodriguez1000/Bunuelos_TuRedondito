# [REQ-F01-02] - PRD: Conexión Universal a Base de Datos (Stage 1.2)

## 1. RESUMEN Y ALINEACIÓN (Overview & Alignment)

### Propósito específico de esta Fase
Garantizar la **integridad, seguridad y disponibilidad** de los datos maestros y transaccionales de **Bunuelos SAS** mediante la implementación de una capa de persistencia técnica robusta. El objetivo es eliminar la fragmentación de accesos a datos y establecer un "Single Point of Truth" (SPoT) para el motor de forecasting, permitiendo que el sistema sea agnóstico a cambios futuros en el proveedor de nube (Neutralidad de Datos **[OBJ-05]**).

### Tabla de Trazabilidad de la Fase
| Entregable | Objetivos Vinculados [OBJ-XX] | Requerimientos de Alto Nivel [REQ-XX] |
| :--- | :--- | :--- |
| Entregable | Objetivos Vinculados [OBJ-XX] | Requerimientos de Alto Nivel [REQ-XX] |
| :--- | :--- | :--- |
| **[DEL-02]** Database Connection | **[OBJ-04]** Automatización Técnica<br>**[OBJ-05]** Neutralidad de Datos | **[REQ-INF-01]** Centralización de Datos en Supabase<br>**[REQ-INF-02]** Acceso Seguro y Encriptado<br>**[REQ-INF-03]** Soporte Multi-Tenant (Standard vs Admin)<br>**[REQ-S3-01]** Configuración de Storage S3 (Supabase) |

---

## 2. ALCANCE ESPECÍFICO DE LA FASE (Scope)

### Qué está INCLUIDO (In Scope)
*   **[REQ-CON-01] Conector Universal:** Desarrollo del módulo `src/connector/db_connector.py` centralizado.
*   **[REQ-SEC-01] Gobernanza de Secretos:** Integración perezosa de variables de entorno (**MEM-ONLY**) mediante `.env` para evitar fugas de seguridad en el repositorio.
*   **[REQ-ARC-01] Dual-Access Client Capability:** Implementación de un proxy de acceso que soporte clientes con RLS restrictivo (Vistas de usuario) y Service Role (Escritura de logs y auditoría).
*   **[REQ-VAL-01] Connectivity Assurance:** Validación de latencia y visibilidad de las fuentes **[DAT-01]** a **[DAT-09]**.
*   **[REQ-S3-01] S3 Cloud Storage:** Configuración de acceso al Bucket S3 de Supabase para el versionamiento de artefactos vía DVC.

### Qué está EXCLUIDO (Out of Scope)
*   Migración de datos (ETL) o limpieza de nulos (Stage 2.3).
*   Configuración de backups o replicación de base de datos.
*   Interfase de usuario (Dashboard) para gestión de base de datos.

---

## 3. CASOS DE USO Y ÉPICAS (User Stories & Epics)

### Épica: Acceso Seguro y Unificado a Datos [EP-01]
*   **User Story 1 (Developer Experience):** Como **Ingeniero de Datos**, quiero invocar una única clase en `src/` que gestione la conexión automáticamente para no repetir la lógica de autenticación en cada script de extracción (Vinculado a **[REQ-CON-01]**).
*   **User Story 2 (Security Compliance):** Como **CISO**, quiero asegurar que el token de rol de servicio solo se use para auditoría y nunca se exponga en el flujo de consulta estándar (Vinculado a **[REQ-SEC-01]**).
*   **User Story 3 (Resilience):** Como **Sistema de Forecasting**, quiero que el conector falle de forma elocuente (`Fail-Fast`) con códigos de error específicos si el servicio cloud no está disponible, ahorrando tiempo de cómputo (Vinculado a **[REQ-VAL-01]**).
*   **User Story 4 (Blob Storage):** Como **Ingeniero de ML**, quiero tener configurado el acceso S3 para poder versionar mis modelos pesados en la nube de Supabase (Vinculado a **[REQ-S3-01]**).

---

## 4. REQUERIMIENTOS TÉCNICOS Y DE DATOS (Data Requirements)

### Interfaz de Datos
*   **Fuentes Soportadas:** El conector debe permitir acceso transparente a las tablas de **Ventas [DAT-01]**, **Ventas Brutas [DAT-02]**, **Ventas Netas [DAT-03]** y fuentes de soporte (**[DAT-04]**-**[DAT-09]**).
*   **Manejo de Estados:** Deben implementarse códigos de error trazables (**`ERR_DB_001`**, etc.) que faciliten el debugging en el pipeline de CI/CD.

---

## 5. INGENIERÍA Y UX DEL DESARROLLADOR (DX)

### Frecuencia y Uso
*   **Invocación:** El conector será la primera pieza en ejecutarse en cada corrida del pipeline diariamente. Debe ser ligero y no bloqueante.
*   **UX del Desarrollador:** La interfaz de la clase debe ser intuitiva:
    ```python
    connector = DBConnector()
    client = connector.get_client() # Conexión estándar
    ```
*   **Eficiencia [ARC-07]:** Se debe forzar el reuso de la conexión mediante un patrón que prevenga la saturación de sockets en el servidor de Supabase.

---

## 6. CRITERIOS DE ACEPTACIÓN Y MÉTRICAS DE LANZAMIENTO (DoD)

### Definición de Hecho (Definition of Done)
1.  **Validación Técnica:** Singleton verificado mediante pruebas de identidad de memoria.
2.  **Validación de Seguridad:** Se confirma que no hay tokens hardcodeados y que `.env.example` está disponible.
3.  **Métrica de Calidad [MET-INF-01]:** El tiempo total de conexión y handshake inicial debe ser inferior a 2 segundos en el 95% de los casos.
4.  **Trazabilidad y Reporte:** Generación del reporte `connector_report.json` con **Doble Persistencia** (Latest + History) en la ruta parametrizada.
5.  **Configuración S3:** Confirmación de acceso al bucket `dvc_Bunuelos_TuRedondito` mediante las credenciales del `.env`.
6.  **Cero Hardcoding:** Validación de que ninguna ruta o nombre de tabla está quemado en el código, usando `config.yaml` como fuente de verdad.

---
*Refinado por Antigravity (Modo B: Estratega de Producto) mediante workflow /manage_project | 2026-03-14*
