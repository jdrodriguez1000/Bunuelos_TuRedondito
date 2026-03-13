---
description: Workflow para la gestión de commits, ramas y sincronización con GitHub y DVC.
---

# WORKFLOW: Sincronización GitHub y DVC (GITHUB_SYNC_WORKFLOW)

Este flujo garantiza que el código y los datos se suban al repositorio siguiendo las reglas de seguridad y estructuración.

## Pasos del Workflow

### 1. Auditoría de Estado
Review de archivos modificados y detección de archivos no deseados.
// turbo
```powershell
git status
if (Get-Command dvc -ErrorAction SilentlyContinue) { dvc status }
```

### 2. Limpieza y Preparación (Staging)
Aplicación de reglas de exclusión y añadido de archivos.
// turbo
```powershell
# Remover archivos accidentales del índice si existen
git rm -r --cached .pytest_cache/ 2>$null
git rm --cached .env 2>$null

# Añadir cambios (respetando .gitignore)
git add .
```

### 3. Commit Estructurado
Generación del mensaje siguiendo el estándar de **Conventional Commits**.
*   Identificar naturaleza del cambio (feat, fix, docs, data, chore).
*   Redactar mensaje en español descriptivo.

### 4. Gestión de Rama y Push
// turbo
Asegurar que se empuja a una rama de trabajo, no a main.
```powershell
$Branch = git branch --show-current
if ($Branch -eq "main") {
    Write-Error "PUSH DIRECTO A MAIN PROHIBIDO. Use una rama de feature/ o bugfix/."
} else {
    # Si hay cambios en DVC, empujar primero a S3
    if (Get-Command dvc -ErrorAction SilentlyContinue) { dvc push }
    git push origin $Branch
}
```

### 5. Creación de Pull Request
Si la tarea está completada, proponer la creación de un PR hacia `main` mediante la herramienta `create_pull_request`.

---
> [!IMPORTANT]
> Nunca olvides el `dvc push` antes del `git push` si has modificado archivos de datos o modelos.
