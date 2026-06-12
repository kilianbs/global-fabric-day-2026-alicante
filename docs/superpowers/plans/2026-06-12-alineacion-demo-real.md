# Alineación del repo con la demo real — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Alinear docs, README y `src/` con la demo real: workspaces GFD_DEV/GFD_PRO, repo ADO "Global Fabric Day" con ramas `dev`/`pro` (sin `main`), carpeta Git `fabric`, entorno de despliegue único `pro`, solo SP con secreto, y los 3 caminos de despliegue.

**Architecture:** Trabajo de coherencia sobre contenido existente: renombrar `src/workspace` → `src/fabric`, borrar ficheros legacy, corregir `parameter.yml` + value set `pro` + los 3 YAML, y reescribir los módulos de la guía. Sin cambios funcionales en los notebooks ni en `PL_Orquestador` (son el export real).

**Tech Stack:** Markdown (guía en español), YAML (Azure Pipelines), fabric-cicd (parameter.yml), JSON (Variable Library).

**Spec:** `docs/superpowers/specs/2026-06-12-alineacion-demo-real-design.md`

**Verificación general (no hay tests automatizados):** cada tarea termina con greps que comprueban presencia/ausencia de los nombres correctos. La Task 16 hace la verificación global.

**Convenciones obligatorias en todo el contenido:**

| Concepto | Valor |
|---|---|
| Workspaces | `GFD_DEV`, `GFD_PRO` |
| Repo ADO | `Global Fabric Day` |
| Ramas | `dev` (default, git-sync con GFD_DEV) y `pro` (despliegue a GFD_PRO). No existe `main` |
| Carpeta Git de Fabric | `fabric` |
| Entorno fabric-cicd | `pro` (único) |
| GUID workspace GFD_DEV | `6b2d8c5d-8eb6-4b89-8f9e-5cfc82bdf2bb` |
| GUID LH_GlobalFabricDay (dev) | `1546a512-5301-4200-a7e8-774ac7cba230` |
| Ítems | `LH_GlobalFabricDay`, `VL_GlobalFabricDay`, `PL_Orquestador`, `SM_GlobalFabricDay`, `RPT_GlobalFabricDay`, `NB_SetDefaultLakehouse`, `NB_LoadTalks`, `NB_ProcessTalks`, `NB_Orquestador`, `NB_LoadTalks_Pipeline`, `NB_ProcessTalks_Pipeline` |
| Variables de la VL | `LAKEHOUSE_ID`, `WORKSPACE_ID`, `LAKEHOUSE_NAME`, `FABRIC_ENV` |
| Variable groups ADO | `fabric_cicd_group_sensitive` (secretos `pro-aztenantid`, `pro-azclientid`, `pro-azspsecret`) y `fabric_cicd_group_non_sensitive` (`proWorkspaceName=GFD_PRO`, `gitDirectory=fabric`) |

**Prohibido que aparezca en docs/src tras el plan:** `GFD26`, `Demo[A-Z]` (DemoNotebook, DemoVariables...), rama `main` como parte del flujo, `Workload Identity`/`Federación` (módulo 05), `.deploy/`, `pre.json`, `main.json`, `fabric-cicd-demo` (nombre de repo), `src/workspace`.

---

### Task 1: Reestructura de src/ (renombrado y borrado de legacy)

**Files:**
- Rename: `src/workspace/` → `src/fabric/`
- Delete: `src/deploy/deploy.py`, `src/deploy/validate.py`, `src/deploy/__pycache__/`, `src/pipelines/azure-pipelines-ci.yml`, `src/pipelines/azure-pipelines-cd.yml`

- [ ] **Step 1: Renombrar la carpeta con git mv**

```bash
git mv src/workspace src/fabric
```

- [ ] **Step 2: Borrar los ficheros legacy**

```bash
git rm src/deploy/deploy.py src/deploy/validate.py src/pipelines/azure-pipelines-ci.yml src/pipelines/azure-pipelines-cd.yml
rm -rf src/deploy/__pycache__
```

- [ ] **Step 3: Verificar el resultado**

Run: `git status --short` y `ls src/`
Expected: `src/` contiene exactamente `fabric/`, `deploy/`, `pipelines/`. En `src/deploy/` quedan `deploy-to-fabric.py`, `deploy-to-fabric-changes.py`, `deploy-to-fabric-selective.py`, `requirements.txt`. En `src/pipelines/` quedan `deploy-to-fabric.yml`, `deploy-to-fabric-changes.yml`, `deploy-to-fabric-selected-items.yml`.

- [ ] **Step 4: Commit**

```bash
git add -A src/
git commit -m "refactor: src/fabric como replica del repo ADO; eliminar deploy/pipelines legacy"
```

---

### Task 2: Value set `pro` y settings.json de la Variable Library

Para que el despliegue a PRO sea 100% automático, `pro.json` debe traer overrides de `WORKSPACE_ID` y `LAKEHOUSE_ID` (con los GUIDs de dev como placeholder, que `parameter.yml` sustituye en despliegue) y `settings.json` debe declarar `activeValueSetName` para que parameter.yml pueda activar `pro`.

**Files:**
- Modify: `src/fabric/VL_GlobalFabricDay.VariableLibrary/valueSets/pro.json`
- Modify: `src/fabric/VL_GlobalFabricDay.VariableLibrary/settings.json`

- [ ] **Step 1: Reescribir pro.json (contenido completo)**

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/variableLibrary/definition/valueSet/1.0.0/schema.json",
  "name": "pro",
  "variableOverrides": [
    {
      "name": "FABRIC_ENV",
      "value": "PRO"
    },
    {
      "name": "WORKSPACE_ID",
      "value": "6b2d8c5d-8eb6-4b89-8f9e-5cfc82bdf2bb"
    },
    {
      "name": "LAKEHOUSE_ID",
      "value": "1546a512-5301-4200-a7e8-774ac7cba230"
    }
  ]
}
```

(Los GUIDs son los de dev a propósito: son el `find_key` que parameter.yml sustituye por `$workspace.$id` y `$items.Lakehouse...$id` al desplegar. `LAKEHOUSE_NAME` no se sobrescribe: es igual en ambos entornos.)

- [ ] **Step 2: Reescribir settings.json (contenido completo)**

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/variableLibrary/definition/settings/1.0.0/schema.json",
  "valueSetsOrder": [
    "pro"
  ],
  "activeValueSetName": "Default value set"
}
```

> Nota para el ejecutor: "Default value set" es el nombre del value set por defecto en Fabric. Si al validar contra el export real del workspace el nombre difiere, usar el del export real.

- [ ] **Step 3: Commit**

```bash
git add src/fabric/VL_GlobalFabricDay.VariableLibrary
git commit -m "fix(vl): overrides de WORKSPACE_ID/LAKEHOUSE_ID en value set pro y activeValueSetName"
```

---

### Task 3: parameter.yml — entorno único `pro`

**Files:**
- Modify: `src/fabric/parameter.yml` (reemplazo completo)

- [ ] **Step 1: Reescribir parameter.yml (contenido completo)**

```yaml
find_replace:

    # ── Workspace ID de GFD_DEV ──
    # Aparece en los META de los notebooks *_Pipeline (lakehouse vinculado)
    - find_value: "6b2d8c5d-8eb6-4b89-8f9e-5cfc82bdf2bb"
      replace_value:
          pro: "$workspace.$id"

    # ── Lakehouse ID de LH_GlobalFabricDay en GFD_DEV ──
    - find_value: "1546a512-5301-4200-a7e8-774ac7cba230"
      replace_value:
          pro: "$items.Lakehouse.LH_GlobalFabricDay.$id"

key_value_replace:

    # ── Referencias de notebooks en PL_Orquestador ──
    - find_key: $.properties.activities[?(@.name=="LoadTalks")].typeProperties.notebookId
      replace_value:
          pro: "$items.Notebook.NB_LoadTalks_Pipeline.$id"
      item_type: "DataPipeline"

    - find_key: $.properties.activities[?(@.name=="ProcessTalks")].typeProperties.notebookId
      replace_value:
          pro: "$items.Notebook.NB_ProcessTalks_Pipeline.$id"
      item_type: "DataPipeline"

    # WorkspaceId en las actividades del pipeline
    - find_key: $.properties.activities[*].typeProperties.workspaceId
      replace_value:
          pro: "$workspace.$id"
      item_type: "DataPipeline"

    # ── Variable Library: value set pro ──
    - find_key: $.variableOverrides[?(@.name=="WORKSPACE_ID")].value
      replace_value:
          pro: "$workspace.$id"
      item_type: "VariableLibrary"
      file_path: "**/valueSets/pro.json"

    - find_key: $.variableOverrides[?(@.name=="LAKEHOUSE_ID")].value
      replace_value:
          pro: "$items.Lakehouse.LH_GlobalFabricDay.$id"
      item_type: "VariableLibrary"
      file_path: "**/valueSets/pro.json"

    # ── Variable Library: activar el value set pro en PRO ──
    - find_key: $.activeValueSetName
      replace_value:
          pro: "pro"
      item_type: "VariableLibrary"
      file_path: "**/settings.json"
```

- [ ] **Step 2: Verificar coherencia de GUIDs**

Run: `grep -rl "6b2d8c5d-8eb6-4b89-8f9e-5cfc82bdf2bb" src/fabric/ | sort` y lo mismo con `1546a512-...`
Expected: ambos GUIDs aparecen en los notebooks `*_Pipeline` (META), en `variables.json`, en `valueSets/pro.json` y en `parameter.yml`. Ningún otro GUID de los antiguos `find_value` (`5b93e2cc...`, `19ff3c27...`) queda en el repo: `grep -r "5b93e2cc\|19ff3c27" src/` no devuelve nada.

- [ ] **Step 3: Commit**

```bash
git add src/fabric/parameter.yml
git commit -m "fix(parameter): entorno unico pro, GUIDs reales y notebooks _Pipeline"
```

---

### Task 4: deploy-to-fabric.yml — deploy de todo (pipeline por defecto)

**Files:**
- Modify: `src/pipelines/deploy-to-fabric.yml` (reemplazo completo)

- [ ] **Step 1: Reescribir el YAML (contenido completo)**

```yaml
# Camino 1 — Deploy de todo (pipeline por defecto).
# Cada cambio en la carpeta fabric/ de la rama pro dispara el pipeline
# y despliega TODOS los items al workspace GFD_PRO.
trigger:
  branches:
    include:
    - pro
  paths:
    include:
    - fabric/**

parameters:
- name: items_in_scope
  displayName: Tipos de items de Fabric a desplegar
  type: string
  default: '["Lakehouse","VariableLibrary","Notebook","DataPipeline","SemanticModel","Report"]'

variables:
  - group: fabric_cicd_group_sensitive
  - group: fabric_cicd_group_non_sensitive

stages:
  - stage: DeployPro
    displayName: "Deploy to PRO"
    jobs:
      - deployment: Deployment
        displayName: "Deploy Resources to PRO"
        environment: pro
        pool:
          vmImage: windows-latest
        strategy:
          runOnce:
            deploy:
              steps:
                # Step 1: Checkout del codigo
                - checkout: self
                # Step 2: Python 3.12
                - task: UsePythonVersion@0
                  inputs:
                    versionSpec: '3.12'
                    addToPath: true
                  displayName: "Set up Python Environment"
                # Step 3: Dependencias
                - script: |
                    python -m pip install --upgrade pip
                    pip install fabric-cicd
                  displayName: "Install Fabric CICD Library"
                # Step 4: Despliegue
                - task: PythonScript@0
                  inputs:
                    scriptSource: filePath
                    scriptPath: 'deploy/deploy-to-fabric.py'
                    arguments: >-
                      --aztenantid $(pro-aztenantid)
                      --azclientid $(pro-azclientid)
                      --azspsecret $(pro-azspsecret)
                      --items_in_scope "${{ parameters.items_in_scope }}"
                      --target_env pro
                  displayName: 'Deploy via fabric-cicd'
```

- [ ] **Step 2: Commit**

```bash
git add src/pipelines/deploy-to-fabric.yml
git commit -m "fix(pipelines): deploy-to-fabric solo rama pro, stage unico, rutas deploy/"
```

---

### Task 5: deploy-to-fabric-changes.yml — deploy de cambios

**Files:**
- Modify: `src/pipelines/deploy-to-fabric-changes.yml` (reemplazo completo)

- [ ] **Step 1: Reescribir el YAML (contenido completo)**

```yaml
# Camino 2 — Deploy de cambios.
# Mismo trigger que el camino 1, pero solo despliega los items que han
# cambiado respecto al ultimo commit (git diff HEAD~1).
# El parametro force_full_deploy permite forzar un despliegue completo.
trigger:
  branches:
    include:
    - pro
  paths:
    include:
    - fabric/**

parameters:
- name: items_in_scope
  displayName: Tipos de items de Fabric a desplegar
  type: string
  default: '["Lakehouse","VariableLibrary","Notebook","DataPipeline","SemanticModel","Report"]'

- name: force_full_deploy
  displayName: Forzar despliegue completo (ignora git diff)
  type: boolean
  default: false

variables:
  - group: fabric_cicd_group_sensitive
  - group: fabric_cicd_group_non_sensitive

stages:
  - stage: DeployPro
    displayName: "Deploy changes to PRO"
    jobs:
      - job: DeploySolution
        pool:
          vmImage: windows-latest
        steps:
          # Step 1: Checkout con historial completo (necesario para git diff)
          - checkout: self
            fetchDepth: 0
            persistCredentials: true

          # Step 2: Python 3.12
          - task: UsePythonVersion@0
            inputs:
              versionSpec: '3.12'
              addToPath: true
            displayName: "Set up Python Environment"

          # Step 3: Dependencias
          - script: |
              python -m pip install --upgrade pip
              pip install fabric-cicd
            displayName: "Install Fabric CICD Library"

          # Despliegue de SOLO CAMBIOS (force_full_deploy = false)
          - task: PythonScript@0
            condition: eq('${{ parameters.force_full_deploy }}', 'false')
            inputs:
              scriptSource: filePath
              scriptPath: 'deploy/deploy-to-fabric-changes.py'
              arguments: >-
                --aztenantid $(pro-aztenantid)
                --azclientid $(pro-azclientid)
                --azspsecret $(pro-azspsecret)
                --items_in_scope "${{ parameters.items_in_scope }}"
                --target_env pro
                --git_compare_ref HEAD~1
            displayName: 'Deploy changed items via fabric-cicd'

          # Despliegue COMPLETO (force_full_deploy = true)
          - task: PythonScript@0
            condition: eq('${{ parameters.force_full_deploy }}', 'true')
            inputs:
              scriptSource: filePath
              scriptPath: 'deploy/deploy-to-fabric-changes.py'
              arguments: >-
                --aztenantid $(pro-aztenantid)
                --azclientid $(pro-azclientid)
                --azspsecret $(pro-azspsecret)
                --items_in_scope "${{ parameters.items_in_scope }}"
                --target_env pro
                --git_compare_ref HEAD~1
                --force_full_deploy
            displayName: 'Full deploy via fabric-cicd'
```

- [ ] **Step 2: Commit**

```bash
git add src/pipelines/deploy-to-fabric-changes.yml
git commit -m "fix(pipelines): deploy-changes solo rama pro, stage unico, rutas deploy/"
```

---

### Task 6: deploy-to-fabric-selected-items.yml — deploy selectivo manual

**Files:**
- Modify: `src/pipelines/deploy-to-fabric-selected-items.yml` (reemplazo completo)

- [ ] **Step 1: Reescribir el YAML (contenido completo)**

```yaml
# Camino 3 — Deploy selectivo.
# Pipeline manual (sin trigger): se indican los items concretos a desplegar,
# separados por comas, con el formato <Nombre>.<Tipo>.
trigger: none

parameters:
  - name: items_to_deploy
    displayName: 'Items a desplegar (separados por comas, formato Nombre.Tipo)'
    type: string
    default: 'NB_SetDefaultLakehouse.Notebook'

  - name: items_in_scope
    displayName: Tipos de items de Fabric en alcance
    type: string
    default: '["Lakehouse","VariableLibrary","Notebook","DataPipeline","SemanticModel","Report"]'

variables:
  - group: fabric_cicd_group_sensitive
  - group: fabric_cicd_group_non_sensitive

stages:
  - stage: DeploySelectivePro
    displayName: "Selective deploy to PRO"
    jobs:
      - deployment: Deployment
        displayName: "Deploy selected items to PRO"
        environment: pro
        pool:
          vmImage: windows-latest
        strategy:
          runOnce:
            deploy:
              steps:
                # Step 1: Checkout del codigo
                - checkout: self
                # Step 2: Python 3.12
                - task: UsePythonVersion@0
                  inputs:
                    versionSpec: '3.12'
                    addToPath: true
                  displayName: "Set up Python Environment"
                # Step 3: Dependencias
                - script: |
                    python -m pip install --upgrade pip
                    pip install fabric-cicd
                  displayName: "Install Fabric CICD Library"
                # Step 4: Despliegue selectivo
                - task: PythonScript@0
                  inputs:
                    scriptSource: filePath
                    scriptPath: 'deploy/deploy-to-fabric-selective.py'
                    arguments: >-
                      --aztenantid $(pro-aztenantid)
                      --azclientid $(pro-azclientid)
                      --azspsecret $(pro-azspsecret)
                      --items_in_scope "${{ parameters.items_in_scope }}"
                      --target_env pro
                      --items_to_deploy "${{ parameters.items_to_deploy }}"
                  displayName: 'Selective deploy via fabric-cicd'
```

- [ ] **Step 2: Verificación de los tres YAML**

Run: `grep -n "pre\|main\|\.deploy" src/pipelines/*.yml`
Expected: sin resultados (ninguna referencia a `pre`, `main` ni `.deploy/`). Y `grep -rn "NB_DefaultLakehouse" src/` sin resultados (el nombre correcto es `NB_SetDefaultLakehouse`). Nota: el ejemplo del mensaje de error en `deploy-to-fabric-selective.py` líneas 48-54 también dice `NB_DefaultLakehouse` — corregirlo a `NB_SetDefaultLakehouse` en el comentario y el ValueError.

- [ ] **Step 3: Corregir el ejemplo en deploy-to-fabric-selective.py**

En `src/deploy/deploy-to-fabric-selective.py`, reemplazar las dos apariciones de `NB_DefaultLakehouse.Notebook` por `NB_SetDefaultLakehouse.Notebook` (comentario de la línea 48 y mensaje del ValueError).

- [ ] **Step 4: Commit**

```bash
git add src/pipelines/deploy-to-fabric-selected-items.yml src/deploy/deploy-to-fabric-selective.py
git commit -m "fix(pipelines): deploy selectivo manual solo a pro con item de ejemplo real"
```

---

### Task 7: README de src/fabric

**Files:**
- Modify: `src/fabric/README.md` (reemplazo completo)

- [ ] **Step 1: Reescribir el README (contenido completo)**

```markdown
# Definiciones de ítems de Fabric

Esta carpeta replica la carpeta `fabric/` del repo de Azure DevOps
**Global Fabric Day**, que el workspace **GFD_DEV** sincroniza mediante
Git integration (rama `dev`).

## Origen de los archivos

Las definiciones **autoritativas** se generan desde Fabric: al hacer commit
desde el workspace GFD_DEV, Fabric escribe aquí el formato Git de cada ítem.
Los archivos de este repo son **implementaciones de referencia** para que
puedas ver el formato antes de construir la demo; al replicarla, tu repo de
ADO contendrá los archivos exportados por tu propio workspace (con tus GUIDs).

## Ítems

| Carpeta | Tipo | Notas |
| --- | --- | --- |
| `VL_GlobalFabricDay.VariableLibrary` | Variable Library | Variables `LAKEHOUSE_ID`, `WORKSPACE_ID`, `LAKEHOUSE_NAME`, `FABRIC_ENV`; value set `pro` |
| `LH_GlobalFabricDay.Lakehouse` | Lakehouse | Vacío; los notebooks crean las tablas |
| `NB_SetDefaultLakehouse.Notebook` | Notebook | Utilitario: vincula el lakehouse en runtime con `%%configure` + Variable Library |
| `NB_LoadTalks.Notebook` | Notebook | Camino 1: `%run NB_SetDefaultLakehouse`, sin IDs hardcodeados |
| `NB_ProcessTalks.Notebook` | Notebook | Camino 1: `%run NB_SetDefaultLakehouse`, sin IDs hardcodeados |
| `NB_LoadTalks_Pipeline.Notebook` | Notebook | Camino 2: lakehouse **vinculado** + parámetros desde el pipeline |
| `NB_ProcessTalks_Pipeline.Notebook` | Notebook | Camino 2: lakehouse **vinculado** + parámetros desde el pipeline |
| `NB_Orquestador.Notebook` | Notebook | Orquestación desde notebook |
| `PL_Orquestador.DataPipeline` | Data Pipeline | Orquesta los notebooks `*_Pipeline` pasando variables de la librería |
| `SM_GlobalFabricDay.SemanticModel` | Modelo semántico | Export desde Fabric (formato TMDL) |
| `RPT_GlobalFabricDay.Report` | Informe | Export desde Fabric (formato PBIR) |

## Los dos caminos de buenas prácticas

1. **Lakehouse en runtime** — `NB_LoadTalks` y `NB_ProcessTalks` empiezan con
   `%run NB_SetDefaultLakehouse`, que lee `LAKEHOUSE_NAME`, `LAKEHOUSE_ID` y
   `WORKSPACE_ID` de la Variable Library y vincula el lakehouse al vuelo.
   Cero GUIDs en el código: no hay nada que reemplazar al desplegar.
2. **Parámetros desde pipeline** — `NB_LoadTalks_Pipeline` y
   `NB_ProcessTalks_Pipeline` tienen el lakehouse **vinculado** en sus
   metadatos y reciben los valores como parámetros desde `PL_Orquestador`
   (`@pipeline().libraryVariables...`). Los GUIDs vinculados son los que
   `parameter.yml` sustituye al desplegar a otro entorno.

## parameter.yml

`parameter.yml` (en esta carpeta, donde fabric-cicd lo espera) hace el resto
al desplegar a `pro`: sustituye los GUIDs de dev por los del workspace
destino, repara las referencias de notebooks del pipeline y activa el value
set `pro` de la Variable Library. Ver módulo 06 de la guía.
```

- [ ] **Step 2: Commit**

```bash
git add src/fabric/README.md
git commit -m "docs: README de src/fabric con items reales y los dos caminos"
```

---

### Task 8: docs/02-workspaces.md

**Files:**
- Modify: `docs/02-workspaces.md`

- [ ] **Step 1: Aplicar los renombrados**

Leer el fichero completo y aplicar en todo el texto:
- `GFD26_DEV` / `GFD26 - Dev` → `GFD_DEV`; `GFD26_PRO` / `GFD26 - Prod` → `GFD_PRO`; prefijo `GFD26` → `GFD`.
- La tabla de GUIDs de ejemplo mantiene los GUIDs (son los reales de la demo): `GFD_DEV` → `6b2d8c5d-8eb6-4b89-8f9e-5cfc82bdf2bb`, `GFD_PRO` → `29679fba-5e38-4a04-8b1b-24342ab63c8f`.
- Donde describa los roles: GFD_DEV conectado a la rama `dev` del repo **Global Fabric Day**; GFD_PRO recibe despliegues del pipeline (sin conexión Git).

- [ ] **Step 2: Verificar**

Run: `grep -n "GFD26\|Demo[A-Z]" docs/02-workspaces.md`
Expected: sin resultados.

- [ ] **Step 3: Commit**

```bash
git add docs/02-workspaces.md
git commit -m "docs(02): workspaces GFD_DEV y GFD_PRO"
```

---

### Task 9: docs/03-contenido-demo.md

**Files:**
- Modify: `docs/03-contenido-demo.md`

- [ ] **Step 1: Leer el fichero y reescribir las secciones**

Cambios obligatorios (manteniendo el tono y el formato de checkpoints/errores típicos del módulo):

1. Workspace de trabajo: `GFD_DEV` en todo el módulo.
2. Sección Variable Library (`VL_GlobalFabricDay`): las 4 variables en MAYÚSCULAS — `LAKEHOUSE_ID`, `WORKSPACE_ID`, `LAKEHOUSE_NAME` (valor `LH_GlobalFabricDay`), `FABRIC_ENV` (valor `DEV`). Value set adicional llamado exactamente `pro` que sobrescribe `FABRIC_ENV=PRO` (y explica que `WORKSPACE_ID`/`LAKEHOUSE_ID` se añadirán como overrides que el despliegue sustituye automáticamente — referencia al módulo 06).
3. Notebooks: describir los seis con sus nombres reales y el propósito de cada uno (tabla de la Task 7 como referencia).
4. Nueva sección **"Dos caminos para vincular el lakehouse"** con este contenido (adaptar la prosa al estilo del módulo):
   - **Camino 1 — Lakehouse en runtime:** `NB_SetDefaultLakehouse` usa `%%configure` con `$(/**/VL_GlobalFabricDay/LAKEHOUSE_NAME)`, `.../LAKEHOUSE_ID` y `.../WORKSPACE_ID`; `NB_LoadTalks` y `NB_ProcessTalks` lo invocan con `%run NB_SetDefaultLakehouse` como primera celda. Ventaja: cero GUIDs hardcodeados, nada que parametrizar en el despliegue.
   - **Camino 2 — Parámetros desde pipeline:** `NB_LoadTalks_Pipeline` y `NB_ProcessTalks_Pipeline` tienen el lakehouse **vinculado** (los GUIDs viajan en los metadatos del notebook) y reciben `FABRIC_ENV`, `WORKSPACE_ID`, `LAKEHOUSE_ID` y `LAKEHOUSE_NAME` como parámetros desde `PL_Orquestador` vía `@pipeline().libraryVariables.*`. El lakehouse vinculado es deliberado: en el módulo 06 se ve cómo `parameter.yml` sustituye esos GUIDs al desplegar.
5. Sección del Data Pipeline: `PL_Orquestador` con dos actividades de notebook (`LoadTalks` → `NB_LoadTalks_Pipeline`, `ProcessTalks` → `NB_ProcessTalks_Pipeline`), conectado a `VL_GlobalFabricDay` en la pestaña de Library variables del pipeline.
6. Modelo semántico e informe: `SM_GlobalFabricDay` y `RPT_GlobalFabricDay`.
7. Checkpoint final actualizado a la lista real de 11 ítems.

- [ ] **Step 2: Verificar**

Run: `grep -n "GFD26\|Demo[A-Z]\|workspace_id\b\|lakehouse_id\b" docs/03-contenido-demo.md`
Expected: sin resultados (las variables aparecen solo en mayúsculas).

- [ ] **Step 3: Commit**

```bash
git add docs/03-contenido-demo.md
git commit -m "docs(03): items reales, VL con 4 variables y los dos caminos de lakehouse"
```

---

### Task 10: docs/04-git-integration.md

**Files:**
- Modify: `docs/04-git-integration.md`

- [ ] **Step 1: Leer el fichero y reescribir**

Cambios obligatorios:

1. Repo de ADO se llama **Global Fabric Day** (no `fabric-cicd-demo`).
2. Ramas: al crear el repo ADO genera una rama inicial; crear `dev` y `pro` y **eliminar `main`** (o renombrar la inicial a `dev`): `dev` queda como **rama por defecto** (Repos > Branches > "..." > Set as default branch). El flujo es `feature/* → dev → pro`; no existe `main`.
3. Conectar GFD_DEV a la rama `dev` con **Git folder = `fabric`** (no `/workspace`). Actualizar también la fila correspondiente de la tabla de errores típicos (carpeta `/` vs `fabric`).
4. La sección de exploración de carpetas usa los ítems reales: `LH_GlobalFabricDay.Lakehouse/` (solo `.platform`), `NB_LoadTalks.Notebook/` (`.platform` + `notebook-content.py`), `VL_GlobalFabricDay.VariableLibrary/` (`.platform`, `variables.json`, `settings.json`, `valueSets/pro.json`). Comparación con `src/fabric/` de este repo (no `src/workspace`).
5. **Nueva sección** (tras el sync inicial): **"Completar el repo desde VS Code"** con este contenido:
   - Clonar el repo en local: botón **Clone** en ADO > **Clone in VS Code** (o `git clone <url>`), rama `dev`.
   - Copiar desde este repo de GitHub: `src/deploy/` → `deploy/` y `src/pipelines/` → `pipelines/` (a la raíz del repo de ADO, junto a `fabric/`), y `src/fabric/parameter.yml` → `fabric/parameter.yml` (junto a los ítems, donde fabric-cicd lo espera).
   - Estructura resultante del repo ADO:
     ```
     Global Fabric Day (rama dev)
     ├── fabric/          # ítems exportados por Fabric + parameter.yml
     ├── deploy/          # scripts Python de despliegue
     └── pipelines/       # YAML de Azure Pipelines
     ```
   - Commit y push a `dev`: `git add . && git commit -m "deploy, pipelines y parameter.yml" && git push`.
   - Nota: Fabric solo sincroniza la carpeta `fabric/`; `deploy/` y `pipelines/` no aparecen en el workspace.
6. Branch-out y PR: igual que ahora pero el PR de promoción es `dev` → `pro`; las **políticas de rama** se configuran sobre `pro` (no `main`).
7. Checkpoint y errores típicos actualizados a los nuevos nombres.

- [ ] **Step 2: Verificar**

Run: `grep -n "GFD26\|Demo[A-Z]\|fabric-cicd-demo\|/workspace\|rama \`main\`" docs/04-git-integration.md`
Expected: sin resultados. (Una mención a borrar/renombrar la rama `main` inicial del repo es aceptable; el flujo no debe usarla.)

- [ ] **Step 3: Commit**

```bash
git add docs/04-git-integration.md
git commit -m "docs(04): repo Global Fabric Day, ramas dev/pro, carpeta fabric y seccion VS Code"
```

---

### Task 11: docs/05-service-principal.md

**Files:**
- Modify: `docs/05-service-principal.md`

- [ ] **Step 1: Leer el fichero y editar**

1. **Eliminar por completo la "Variante B — Federación (Workload Identity)"** y cualquier mención a federación, service connection federada o `AzureCliCredential` como variante. Queda una única vía: SP con secreto (`ClientSecretCredential`). Quitar también el encabezado "Variante A" si queda como única (renombrar la sección a algo como "Autenticación con secreto de cliente").
2. Renombrados: workspace `GFD_PRO` (rol Admin del SP), nombres de ítems reales si aparecen.
3. Checkpoint y errores típicos: eliminar las entradas relativas a federación.

- [ ] **Step 2: Verificar**

Run: `grep -in "federa\|workload identity\|variante b\|AzureCliCredential\|GFD26" docs/05-service-principal.md`
Expected: sin resultados.

- [ ] **Step 3: Commit**

```bash
git add docs/05-service-principal.md
git commit -m "docs(05): eliminar variante de federacion; solo SP con secreto"
```

---

### Task 12: docs/06-fabric-cicd.md

**Files:**
- Modify: `docs/06-fabric-cicd.md`

- [ ] **Step 1: Leer el fichero y editar**

1. Renombrados generales: `GFD_DEV`/`GFD_PRO`, ítems reales, rutas `fabric/` (repository_directory) y `deploy/`.
2. La explicación de `parameter.yml` debe reflejar el contenido de la Task 3: entorno único `pro`; `find_replace` de los dos GUIDs de dev (con la explicación de que aparecen en los META de los notebooks `*_Pipeline` por el lakehouse vinculado); `key_value_replace` para los `notebookId` de `PL_Orquestador`, los overrides del value set `pro` y la activación de `activeValueSetName`. Mensaje clave: el value set `pro` del repo lleva los GUIDs de dev como placeholder y fabric-cicd los sustituye por los reales de PRO al desplegar — no hay que tocarlos a mano.
3. Tabla de GUIDs a sustituir: el GUID de ejemplo del workspace es el de GFD_DEV (`6b2d8c5d-...`), el del lakehouse `1546a512-...`.
4. La prueba local despliega a `GFD_PRO` con `--target_env pro` usando el script `deploy/deploy-to-fabric.py` (ajustar el comando de ejemplo a los argumentos reales del script: `--aztenantid`, `--azclientid`, `--azspsecret`, `--items_in_scope`, `--target_env`; indicar que en local hay que exportar `PROWORKSPACENAME=GFD_PRO` y `GITDIRECTORY=fabric` como variables de entorno porque el script las lee de ahí).
5. Checkpoint actualizado.

- [ ] **Step 2: Verificar**

Run: `grep -n "GFD26\|Demo[A-Z]\|pre\.json\|main\.json\|src/workspace" docs/06-fabric-cicd.md`
Expected: sin resultados.

- [ ] **Step 3: Commit**

```bash
git add docs/06-fabric-cicd.md
git commit -m "docs(06): parameter.yml con entorno pro y prueba local alineada"
```

---

### Task 13: docs/07-pipelines-ado.md — los 3 caminos

**Files:**
- Modify: `docs/07-pipelines-ado.md` (reescritura sustancial)

- [ ] **Step 1: Leer el fichero y reescribir alrededor de los 3 caminos**

Estructura objetivo del módulo (manteniendo tono, checkpoints y errores típicos):

1. **Preparación común:**
   - Variable groups: `fabric_cicd_group_sensitive` (secretos: `pro-aztenantid`, `pro-azclientid`, `pro-azspsecret`) y `fabric_cicd_group_non_sensitive` (`proWorkspaceName` = `GFD_PRO`, `gitDirectory` = `fabric`). Explicar la convención del script: `{entorno}WorkspaceName`.
   - Environment de ADO llamado `pro` con **aprobación manual** (momento estrella de la demo).
2. **Los 3 caminos** (una sección por camino, cada una referenciando su YAML y su script):

   | Camino | Fichero | Trigger | Qué despliega |
   |---|---|---|---|
   | Deploy de todo | `pipelines/deploy-to-fabric.yml` | Automático: cambios en `fabric/**` de la rama `pro` | Todos los ítems (pipeline por defecto de la demo) |
   | Deploy de cambios | `pipelines/deploy-to-fabric-changes.yml` | Automático: igual que el anterior | Solo los ítems con diff respecto al último commit (`git diff HEAD~1`); `force_full_deploy` para forzar todo |
   | Deploy selectivo | `pipelines/deploy-to-fabric-selected-items.yml` | Manual (`trigger: none`) | Solo los ítems indicados por nombre, separados por comas (`NB_SetDefaultLakehouse.Notebook, RPT_GlobalFabricDay.Report`) |

   Para cada camino: cuándo usarlo (todo = simple y seguro para repos pequeños; cambios = repos grandes o despliegues frecuentes, con la advertencia de dependencias entre ítems y los feature flags experimentales `enable_experimental_features`/`enable_items_to_include`; selectivo = hotfixes y despliegues quirúrgicos).
3. **Registro de pipelines en ADO:** crear los tres en Pipelines > New pipeline > Azure Repos Git > YAML existente; el **pipeline por defecto** de la demo es `deploy-to-fabric.yml`. Nota: si se registran los dos automáticos a la vez, ambos dispararán con cada push a `pro` — para la demo, deshabilitar el trigger del que no se esté mostrando (Pipeline settings > Disabled) o registrar solo uno.
4. **Build validation sobre `pro`:** la política de rama de `pro` puede exigir PR; sin CI de validación (eliminado del repo).
5. Checkpoint: los tres pipelines registrados, variable groups creados, environment `pro` con aprobador.

- [ ] **Step 2: Verificar**

Run: `grep -n "GFD26\|Demo[A-Z]\|azure-pipelines-ci\|azure-pipelines-cd\|validate.py\|rama \`main\`\|federada" docs/07-pipelines-ado.md`
Expected: sin resultados.

- [ ] **Step 3: Commit**

```bash
git add docs/07-pipelines-ado.md
git commit -m "docs(07): los tres caminos de despliegue a pro"
```

---

### Task 14: docs/08-flujo-completo.md

**Files:**
- Modify: `docs/08-flujo-completo.md`

- [ ] **Step 1: Leer el fichero y reescribir el recorrido**

Recorrido end-to-end actualizado:

1. Branch-out desde GFD_DEV (`feature/demo-gfd` a partir de `dev`).
2. Cambio visible en un notebook (p. ej. `NB_LoadTalks`: añadir una columna) — actualizar los nombres de ítems en los pasos de verificación (`NB_LoadTalks`, `PL_Orquestador`, `RPT_GlobalFabricDay`).
3. PR `feature/demo-gfd` → `dev`, merge, **Update from Git** en GFD_DEV.
4. PR `dev` → `pro` (el evento de promoción; no existe `main`).
5. El merge dispara `deploy-to-fabric.yml` (el pipeline por defecto); aprobación manual en el environment `pro`; fabric-cicd publica en GFD_PRO.
6. Verificación en GFD_PRO: ejecutar `PL_Orquestador` o abrir `RPT_GlobalFabricDay`.
7. **Eliminar la sección de actualizar a mano los GUIDs del value set** (pasos "copia el GUID de la URL... edita el value set Prod"): ya no aplica porque `parameter.yml` sustituye `WORKSPACE_ID`/`LAKEHOUSE_ID` del value set `pro` automáticamente en cada despliegue. Sustituirla por un párrafo breve que explique ese mecanismo (con referencia al módulo 06).
8. Mencionar (breve) que los otros dos caminos del módulo 07 (changes y selectivo) se pueden enseñar como variantes: re-ejecutar con un solo ítem cambiado o lanzar el selectivo a mano.
9. Tabla de errores: actualizar referencias (rol del SP en GFD_PRO, etc.).

- [ ] **Step 2: Verificar**

Run: `grep -n "GFD26\|Demo[A-Z]\|rama \`main\`\|value set \`Prod\`" docs/08-flujo-completo.md`
Expected: sin resultados.

- [ ] **Step 3: Commit**

```bash
git add docs/08-flujo-completo.md
git commit -m "docs(08): flujo dev->pro con sustitucion automatica del value set"
```

---

### Task 15: README.md portada y docs/01-prerrequisitos.md

**Files:**
- Modify: `README.md`
- Modify: `docs/01-prerrequisitos.md` (solo si contiene nombres antiguos)

- [ ] **Step 1: Leer README.md y actualizar**

1. Diagrama del flujo: ramas `feature/* → dev → pro` (sin `main`), workspaces GFD_DEV/GFD_PRO, los 3 pipelines de despliegue.
2. Estructura del repo: `src/fabric/`, `src/deploy/` (3 scripts), `src/pipelines/` (3 YAML).
3. Cualquier mención a ítems `Demo*`, `GFD26`, variante federada o CI de validación: actualizar o eliminar.

- [ ] **Step 2: Revisar docs/01-prerrequisitos.md**

Run: `grep -n "GFD26\|Demo[A-Z]\|main\|federa" docs/01-prerrequisitos.md`
Si hay resultados, aplicar los mismos renombrados.

- [ ] **Step 3: Commit**

```bash
git add README.md docs/01-prerrequisitos.md
git commit -m "docs: portada y prerrequisitos alineados con la demo real"
```

---

### Task 16: Verificación global

**Files:** ninguno nuevo (correcciones puntuales si los greps fallan).

- [ ] **Step 1: Greps de términos prohibidos**

```bash
grep -rn "GFD26" docs/ src/ README.md
grep -rn "Demo[A-Z]" docs/ src/ README.md
grep -rn "fabric-cicd-demo" docs/ src/ README.md
grep -rn "\.deploy/" docs/ src/
grep -rn "pre\.json\|main\.json" docs/ src/
grep -rin "workload identity\|federa" docs/05-service-principal.md
grep -rn "src/workspace" docs/ README.md
grep -rn "NB_DefaultLakehouse" docs/ src/
```

Expected: todos sin resultados. (Excluir `docs/superpowers/` de la comprobación: specs y planes históricos pueden contener los nombres antiguos.)

- [ ] **Step 2: Greps de presencia (sanity)**

```bash
grep -rln "GFD_DEV" docs/ | wc -l        # >= 5 modulos
grep -rln "GFD_PRO" docs/ | wc -l        # >= 5 modulos
grep -c "pro:" src/fabric/parameter.yml   # 8 (uno por regla)
grep -rn "rama \`pro\`" docs/ | wc -l    # >= 3
```

- [ ] **Step 3: Comprobar enlaces internos**

```bash
grep -rno "\[[^]]*\]([^)#]*\.md[^)]*)" README.md docs/0*.md | grep -o "([^)]*)" | sort -u
```

Verificar que cada ruta relativa apunta a un fichero existente (especial atención a enlaces a `src/workspace` que deben ser `src/fabric`).

- [ ] **Step 4: Commit final (si hubo correcciones)**

```bash
git add -A
git commit -m "chore: verificacion global de coherencia tras la alineacion"
```
