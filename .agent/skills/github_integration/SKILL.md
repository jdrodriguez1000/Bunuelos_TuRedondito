---
name: github_integration
description: Especialista en control de versiones, orquestación de commits convencionales y gestión de flujo de trabajo en GitHub (GitOps).
---

# Skill: Integración y GitOps (GitHub)

Esta habilidad permite al agente gestionar el ciclo de vida del código y la documentación, asegurando que los avances de **Bunuelos SAS** estén respaldados y versionados de forma segura.

## 🛠️ 1. Capacidades Principales

### A. Gestión de Repositorio Local y Data Control
- Audita el estado de los archivos (`git status` y `dvc status`).
- Aplica limpiezas proactivas para evitar fugas de secretos o archivos pesados.
- Sincroniza punteros `.dvc` con el estado del dataset local.

### B. Versionamiento Estructurado
- Crea ramas orientadas a objetivos específicos alineados con el [Project Plan](../../../docs/artifacts/project_plan.md).
- Usa prefijo `data:` para commits que actualizan versiones de datasets gestionados por DVC.
- Redacta mensajes bajo el estándar **Conventional Commits** en español.

### C. Operación Remota (GitHub)
- Interactúa con GitHub para la creación de Pull Requests y sincronización de cambios.
- **Orquestación S3/Remote**: Ejecuta `dvc push` proactivamente antes de realizar el push de Git.

## 📋 2. Procedimiento de Seguridad Pre-Push
1.  **Escaneo de Secretos**: Revisión de staging para detectar credenciales (.env, tokens).
2.  **Protección de Data-Heavies**: Garantizar que archivos >5MB (o datos) estén fuera del radar de Git y bajo DVC.
3.  **Verificación de Rama**: Confirmar que no se está operando directamente en `main` para commits de desarrollo.

## ⚠️ Restricciones
- **PROHIBIDO** el comando `git push origin main` para desarrollo cotidiano.
- **PROHIBIDO** ignorar conflictos de merge; requiere intervención o resolución explícita.
