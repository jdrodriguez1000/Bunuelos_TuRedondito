# 📜 Reglas del Asistente IA - Bunuelos_TuRedondito

Este documento establece el protocolo de interacción para maximizar la eficiencia técnica y la optimización de recursos en el proyecto.

## 1. 🚀 Optimización de Cuota y Recursos
- **Concisión Directa:** Evitar explicaciones redundantes o cortesías innecesarias. El foco debe ser la solución técnica o el bloque de código solicitado.
- **Contextualización Selectiva:** Solo leer archivos que sean estrictamente necesarios para la tarea actual, priorizando aquellos invocados explícitamente mediante `@` o rutas absolutas.
- **Protocolo Anti-Bucles:** Si un error en la terminal persiste tras 2 intentos de corrección, el asistente **debe detenerse** y solicitar intervención humana para evitar el consumo innecesario de tokens.

## 2. 🧠 Manejo de Estado (Handoff)
- **Inicio de Sesión (Context Loading):** Al iniciar cualquier chat nuevo, el asistente tiene el **mandato obligatorio** de buscar y procesar el archivo `handoff.md` en la raíz del proyecto. Este archivo provee la "memoria de corto plazo" necesaria para continuar sin releer historiales pasados.
- **Persistencia de Sesión:** Ninguna sesión se considera concluida sin la ejecución del workflow `/handoff`. El asistente debe recordar al usuario la actualización del estado si detecta un cierre inminente de jornada o cambio de contexto mayor.

## 3. 🛠️ Estándares de Ingeniería de Software
- **Integridad del Código:** Solo se modificarán los archivos indicados explícitamente. Se respetarán los comentarios preexistentes a menos que su remoción sea necesaria para el refactor solicitado.
- **Consenso Arquitectónico:** Cambios estructurales, modificaciones en el esquema de base de datos o alteraciones en el flujo del Pipeline de ML requieren confirmación explícita previa a su implementación.
- **Trazabilidad:** Cada cambio realizado debe ser capaz de ser justificado bajo el prisma de la reducción del MAPE u optimización operativa del Pipeline.

---
*Ultima actualización: 2026-03-16*
