---
description: Generación automática del estado de sesión (handoff) para optimizar cuota de IA.
---

Este flujo de trabajo se utiliza al finalizar una jornada o tarea para encapsular el contexto actual y permitir que una nueva sesión comience de forma limpia y eficiente.

### Pasos de Ejecución:

1. **Análisis de Sesión**:
   - Revisa el historial de mensajes y los cambios realizados en los archivos durante la sesión actual.
   - Identifica los problemas resueltos y las decisiones arquitectónicas tomadas.

2. **Generación del Reporte**:
   - Crea o actualiza el archivo `handoff.md` en la raíz del proyecto con la siguiente estructura:
     ```markdown
     # 🏁 Handoff - Estado de Sesión
     **Fecha:** [FECHA ACTUAL]
     **Último Commit/Tarea:** [Resumen breve]

     ## 1. ✅ Logros y Problemas Resueltos
     - [Lista de archivos modificados y por qué]
     - [Bugs corregidos o features implementadas]

     ## 2. 🏗️ Estado Actual del Proyecto
     - **Funciona:** [Componentes estables]
     - **En Proceso:** [Tareas a medias o archivos abiertos]

     ## 3. 🎯 Próximos Pasos (Next Session)
     - [ ] Tarea prioritaria 1
     - [ ] Tarea prioritaria 2

     ## 4. 🧠 Decisiones Arquitectónicas
     - [Justificación de cambios estructurales]
     ```

3. **Cierre de Ciclo**:
   - Confirma al usuario que el archivo ha sido guardado.
   - Sugiere al usuario abrir un chat nuevo para la próxima interacción para ahorrar cuota.

// turbo
4. **Verificación**:
   - Ejecuta un comando para verificar que el archivo `handoff.md` existe y tiene contenido.
   - `dir handoff.md`
