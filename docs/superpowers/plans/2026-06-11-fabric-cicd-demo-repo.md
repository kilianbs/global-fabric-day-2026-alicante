# Fabric CI/CD Demo Repo — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construir el repo público de la charla "Microsoft Fabric CI/CD" (Global Fabric Day 2026 Alicante): guía replicable en español (8 módulos) + contenido de la demo (definiciones de ítems, `deploy.py` con fabric-cicd, `parameter.yml`, YAMLs de Azure DevOps).

**Architecture:** Repo de contenido estático sin código ejecutable en CI propio. `src/` replica 1:1 el repo de Azure DevOps que usará la demo real: `src/workspace/` (definiciones de ítems en formato Git de Fabric), `src/deploy/` (script fabric-cicd + parámetros), `src/pipelines/` (YAML de ADO). `docs/` contiene la guía modular en español. Spec aprobado: `docs/superpowers/specs/2026-06-11-fabric-cicd-demo-repo-design.md`.

**Tech Stack:** Markdown (español), Python 3.12 + fabric-cicd, Azure DevOps Pipelines YAML, formato Git de ítems de Fabric (Notebook, VariableLibrary, Lakehouse, DataPipeline, SemanticModel, Report).

**Convenciones globales:**
- Workspaces: `GFD26 - Dev` y `GFD26 - Prod`. Ramas: `feature/*` → `dev` → `main`.
- Entorno fabric-cicd para Prod: cadena `PROD` (mayúsculas, coincide con claves de `parameter.yml`).
- Dataset demo: `https://raw.githubusercontent.com/microsoft/fabric-samples/main/docs-samples/data-engineering/dimension_customer.csv` (CSV público, sin auth).
- GUIDs de Dev en `src/`: se usa el marcador literal `00000000-0000-0000-0000-000000000000`; el módulo 06 de la guía indica sustituirlos por los GUIDs reales del workspace Dev del lector. No es un placeholder del plan: es configuración del usuario.
- Los archivos de `src/workspace/` son **implementaciones de referencia**: una vez montada la demo real en Fabric, el autor los sustituye por el export real (commit de Git integration). Los módulos 03 y 04 de la guía documentan ese flujo. `SemanticModel` y `Report` solo existen vía export (no se escriben a mano); `src/workspace/README.md` lo explica.
- Verificación de cada doc: los enlaces relativos apuntan a archivos existentes del repo (comprobar con Grep/ls), y los bloques de código tienen lenguaje declarado.
- Commit al final de cada tarea.

---

### Task 1: `src/deploy/` — script de despliegue y parámetros

**Files:**
- Create: `src/deploy/deploy.py`
- Create: `src/deploy/parameter.yml`
- Create: `src/deploy/requirements.txt`

- [ ] **Step 1: Crear `src/deploy/requirements.txt`**

```text
fabric-cicd>=0.1.20
azure-identity>=1.17.0
```

- [ ] **Step 2: Crear `src/deploy/deploy.py`**

```python
"""Despliegue de ítems de Fabric con fabric-cicd.

Uso:
  python deploy.py --workspace-id <GUID> --environment PROD --auth secret
  python deploy.py --workspace-id <GUID> --environment PROD --auth cli

Auth "secret": requiere AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET.
Auth "cli": usa la sesión activa de Azure CLI (variante federada vía AzureCLI@2).
"""

import argparse
import os
import sys

from azure.identity import AzureCliCredential, ClientSecretCredential
from fabric_cicd import FabricWorkspace, publish_all_items, unpublish_all_orphan_items

ITEM_TYPES = [
    "VariableLibrary",
    "Lakehouse",
    "Notebook",
    "DataPipeline",
    "SemanticModel",
    "Report",
]


def build_credential(auth_mode: str):
    if auth_mode == "secret":
        for var in ("AZURE_TENANT_ID", "AZURE_CLIENT_ID", "AZURE_CLIENT_SECRET"):
            if not os.environ.get(var):
                sys.exit(f"Falta la variable de entorno {var}")
        return ClientSecretCredential(
            tenant_id=os.environ["AZURE_TENANT_ID"],
            client_id=os.environ["AZURE_CLIENT_ID"],
            client_secret=os.environ["AZURE_CLIENT_SECRET"],
        )
    return AzureCliCredential()


def main() -> None:
    parser = argparse.ArgumentParser(description="Despliega ítems de Fabric con fabric-cicd")
    parser.add_argument("--workspace-id", required=True, help="GUID del workspace destino")
    parser.add_argument("--environment", required=True, help="Entorno destino, p. ej. PROD")
    parser.add_argument("--auth", choices=["secret", "cli"], default="secret")
    parser.add_argument(
        "--repository-directory",
        default=os.path.join(os.path.dirname(__file__), "..", "workspace"),
        help="Carpeta con las definiciones de ítems",
    )
    args = parser.parse_args()

    workspace = FabricWorkspace(
        workspace_id=args.workspace_id,
        environment=args.environment,
        repository_directory=os.path.abspath(args.repository_directory),
        item_type_in_scope=ITEM_TYPES,
        token_credential=build_credential(args.auth),
    )

    publish_all_items(workspace)
    unpublish_all_orphan_items(workspace)


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Verificar sintaxis**

Run: `python -m py_compile src/deploy/deploy.py`
Expected: sin salida, exit 0. (Si no hay Python local, revisar a mano que no haya errores obvios y anotarlo en el commit.)

- [ ] **Step 4: Crear `src/workspace/parameter.yml`**

fabric-cicd busca `parameter.yml` en `repository_directory` (que `deploy.py` apunta a `../workspace`), así que el archivo vive en `src/workspace/`, junto a las definiciones — **no** en `src/deploy/`. El marcador `00000000-...` es el GUID del lakehouse en Dev; el lector lo sustituye siguiendo el módulo 06.

```yaml
# Parametrización por entorno para fabric-cicd.
# 1) Activa el value set de la Variable Library según el entorno destino.
# 2) find/replace residual: la conexión del modelo Direct Lake va incrustada
#    por GUID en la definición y no puede resolverse con variables en runtime.

key_value_replace:
  - find_key: $.activeValueSetName
    replace_value:
      PROD: "Prod"
    item_type: "VariableLibrary"
    item_name: "DemoVariables"

find_replace:
  # GUID del lakehouse de Dev -> GUID del lakehouse en el workspace destino
  - find_value: "00000000-0000-0000-0000-000000000000"
    replace_value:
      PROD: "$items.Lakehouse.DemoLakehouse.$id"
  # GUID del workspace Dev -> workspace destino
  - find_value: "11111111-1111-1111-1111-111111111111"
    replace_value:
      PROD: "$workspace.$id"
```

- [ ] **Step 5: Verificar YAML**

Run: `python -c "import yaml,sys; yaml.safe_load(open('src/workspace/parameter.yml', encoding='utf-8')); print('OK')"`
Expected: `OK`. (Si PyYAML no está instalado: `pip install pyyaml`.)

- [ ] **Step 6: Commit**

```bash
git add src/deploy/ src/workspace/parameter.yml
git commit -m "feat: deploy.py con fabric-cicd y parameter.yml (value sets + find_replace)"
```

---

### Task 2: `src/pipelines/` — YAML de Azure DevOps

**Files:**
- Create: `src/pipelines/azure-pipelines-ci.yml`
- Create: `src/pipelines/azure-pipelines-cd.yml`
- Create: `src/deploy/validate.py`

- [ ] **Step 1: Crear `src/deploy/validate.py`** (validación ligera usada por el CI)

```python
"""Validación ligera del repo antes de mergear a main.

- parameter.yml es YAML válido y solo usa claves soportadas.
- Cada carpeta de ítem en workspace/ contiene un archivo .platform.
"""

import sys
from pathlib import Path

import yaml

WORKSPACE_DIR = Path(__file__).resolve().parent.parent / "workspace"
ALLOWED_KEYS = {"find_replace", "key_value_replace", "spark_pool"}


def validate_parameter_file() -> list[str]:
    errors = []
    param_file = WORKSPACE_DIR / "parameter.yml"
    if not param_file.exists():
        return [f"No existe {param_file}"]
    data = yaml.safe_load(param_file.read_text(encoding="utf-8"))
    unknown = set(data) - ALLOWED_KEYS
    if unknown:
        errors.append(f"Claves no soportadas en parameter.yml: {sorted(unknown)}")
    for entry in data.get("find_replace", []):
        if "find_value" not in entry or "replace_value" not in entry:
            errors.append(f"find_replace incompleto: {entry}")
    for entry in data.get("key_value_replace", []):
        if "find_key" not in entry or "replace_value" not in entry:
            errors.append(f"key_value_replace incompleto: {entry}")
    return errors


def validate_item_folders() -> list[str]:
    errors = []
    for folder in WORKSPACE_DIR.iterdir():
        if folder.is_dir() and "." in folder.name:
            if not (folder / ".platform").exists():
                errors.append(f"Falta .platform en {folder.name}")
    return errors


if __name__ == "__main__":
    all_errors = validate_parameter_file() + validate_item_folders()
    for err in all_errors:
        print(f"ERROR: {err}")
    if all_errors:
        sys.exit(1)
    print("Validación OK")
```

- [ ] **Step 2: Crear `src/pipelines/azure-pipelines-ci.yml`**

En Azure Repos los PR no se disparan con `pr:` del YAML — se configura como **build validation** en la política de rama de `main` (el módulo 07 lo explica). El trigger queda en `none`.

```yaml
# CI ligero: se ejecuta como build validation en los PR hacia main.
# Configurar en: Repos > Branches > main > Branch policies > Build validation.
trigger: none

pool:
  vmImage: ubuntu-latest

steps:
  - checkout: self

  - task: UsePythonVersion@0
    inputs:
      versionSpec: "3.12"
    displayName: Python 3.12

  - script: pip install pyyaml
    displayName: Instalar dependencias

  - script: python deploy/validate.py
    displayName: Validar parameter.yml y estructura de items
```

- [ ] **Step 3: Crear `src/pipelines/azure-pipelines-cd.yml`**

```yaml
# CD: se dispara al mergear a main y despliega al workspace Prod con fabric-cicd.
# Variables esperadas (variable group "fabric-cicd-demo"):
#   PROD_WORKSPACE_ID         GUID del workspace "GFD26 - Prod"
#   AZURE_TENANT_ID           (solo variante "secret")
#   AZURE_CLIENT_ID           (solo variante "secret")
#   AZURE_CLIENT_SECRET       (solo variante "secret", marcada como secreta)
# Variante federada: requiere la service connection "sc-fabric-cicd-demo"
# (Workload Identity Federation) y authMode: federated.

trigger:
  branches:
    include: [main]
  paths:
    include:
      - workspace/**
      - deploy/**

parameters:
  - name: authMode
    displayName: Modo de autenticación
    type: string
    default: secret
    values: [secret, federated]

variables:
  - group: fabric-cicd-demo

stages:
  - stage: DeployProd
    displayName: Desplegar a Prod
    jobs:
      - deployment: fabric_prod
        displayName: fabric-cicd -> GFD26 - Prod
        environment: fabric-prod   # Environment de ADO con aprobación manual
        pool:
          vmImage: ubuntu-latest
        strategy:
          runOnce:
            deploy:
              steps:
                - checkout: self

                - task: UsePythonVersion@0
                  inputs:
                    versionSpec: "3.12"
                  displayName: Python 3.12

                - script: pip install -r deploy/requirements.txt
                  displayName: Instalar fabric-cicd

                # ── Variante A: Service Principal con secreto ──
                - ${{ if eq(parameters.authMode, 'secret') }}:
                    - script: >
                        python deploy/deploy.py
                        --workspace-id $(PROD_WORKSPACE_ID)
                        --environment PROD
                        --auth secret
                      displayName: Desplegar (SP con secreto)
                      env:
                        AZURE_TENANT_ID: $(AZURE_TENANT_ID)
                        AZURE_CLIENT_ID: $(AZURE_CLIENT_ID)
                        AZURE_CLIENT_SECRET: $(AZURE_CLIENT_SECRET)

                # ── Variante B: federada (Workload Identity) ──
                - ${{ if eq(parameters.authMode, 'federated') }}:
                    - task: AzureCLI@2
                      displayName: Desplegar (SP federado)
                      inputs:
                        azureSubscription: sc-fabric-cicd-demo
                        scriptType: bash
                        scriptLocation: inlineScript
                        inlineScript: >
                          python deploy/deploy.py
                          --workspace-id $(PROD_WORKSPACE_ID)
                          --environment PROD
                          --auth cli
```

- [ ] **Step 4: Verificar YAML y Python**

Run:
```bash
python -m py_compile src/deploy/validate.py
python -c "import yaml; yaml.safe_load(open('src/pipelines/azure-pipelines-ci.yml', encoding='utf-8')); yaml.safe_load(open('src/pipelines/azure-pipelines-cd.yml', encoding='utf-8')); print('OK')"
```
Expected: `OK`. Nota: las expresiones `${{ if }}` son válidas en ADO; PyYAML las parsea como strings sin error.

- [ ] **Step 5: Commit**

```bash
git add src/pipelines/ src/deploy/validate.py
git commit -m "feat: pipelines de ADO (CI build-validation y CD a Prod) + validate.py"
```

---

### Task 3: `src/workspace/` — definiciones de referencia de los ítems

**Files:**
- Create: `src/workspace/README.md`
- Create: `src/workspace/DemoNotebook.Notebook/.platform`
- Create: `src/workspace/DemoNotebook.Notebook/notebook-content.py`
- Create: `src/workspace/DemoVariables.VariableLibrary/.platform`
- Create: `src/workspace/DemoVariables.VariableLibrary/variables.json`
- Create: `src/workspace/DemoVariables.VariableLibrary/valueSets/Prod.json`
- Create: `src/workspace/DemoVariables.VariableLibrary/settings.json`
- Create: `src/workspace/DemoLakehouse.Lakehouse/.platform`
- Create: `src/workspace/DemoPipeline.DataPipeline/.platform`
- Create: `src/workspace/DemoPipeline.DataPipeline/pipeline-content.json`

- [ ] **Step 1: Crear `src/workspace/README.md`**

```markdown
# Definiciones de ítems de Fabric

Esta carpeta replica el contenido del repo de Azure DevOps que el workspace
**GFD26 - Dev** sincroniza mediante Git integration (rama `dev`).

## Origen de los archivos

Las definiciones **autoritativas** se generan desde Fabric: al hacer commit
desde el workspace Dev, Fabric escribe aquí el formato Git de cada ítem.
Los archivos de este repo son **implementaciones de referencia** para que
puedas ver el formato antes de construir la demo; al replicarla, tu repo de
ADO contendrá los archivos exportados por tu propio workspace.

## Ítems

| Carpeta | Tipo | Notas |
| --- | --- | --- |
| `DemoVariables.VariableLibrary` | Variable Library | Value sets `Default` (=Dev) y `Prod` |
| `DemoLakehouse.Lakehouse` | Lakehouse | Vacío; el notebook crea las tablas |
| `DemoNotebook.Notebook` | Notebook | Ingesta CSV -> tabla Delta |
| `DemoPipeline.DataPipeline` | Data Pipeline | Orquesta el notebook usando variables de la librería |
| `DemoModel.SemanticModel` | Modelo semántico | **Solo vía export** desde Fabric (formato TMDL) |
| `DemoReport.Report` | Informe | **Solo vía export** desde Fabric (formato PBIR) |

`DemoModel.SemanticModel` y `DemoReport.Report` no se incluyen a mano: créalos
en el workspace Dev (módulo 03 de la guía) y haz commit desde Fabric para
obtener sus definiciones.

`parameter.yml` (en esta carpeta) lo usa fabric-cicd al desplegar: activa el
value set `Prod` y sustituye los GUIDs residuales. Ver módulo 06.
```

- [ ] **Step 2: Crear `DemoNotebook.Notebook/.platform`**

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
  "metadata": {
    "type": "Notebook",
    "displayName": "DemoNotebook",
    "description": "Ingesta del CSV de clientes y escritura como tabla Delta"
  },
  "config": {
    "version": "2.0",
    "logicalId": "aaaaaaaa-0000-4000-8000-000000000001"
  }
}
```

- [ ] **Step 3: Crear `DemoNotebook.Notebook/notebook-content.py`**

```python
# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "00000000-0000-0000-0000-000000000000",
# META       "default_lakehouse_name": "DemoLakehouse",
# META       "default_lakehouse_workspace_id": "11111111-1111-1111-1111-111111111111"
# META     }
# META   }
# META }

# CELL ********************

# Descarga el dataset público de clientes y lo carga como DataFrame de Spark
import pandas as pd

CSV_URL = (
    "https://raw.githubusercontent.com/microsoft/fabric-samples/main/"
    "docs-samples/data-engineering/dimension_customer.csv"
)

pdf = pd.read_csv(CSV_URL)
df = spark.createDataFrame(pdf)
print(f"Filas leídas: {df.count()}")

# CELL ********************

# Limpieza mínima: normaliza nombres de columna a snake_case
for col in df.columns:
    df = df.withColumnRenamed(col, col.strip().replace(" ", "_").lower())

# CELL ********************

# Escribe la tabla Delta en el lakehouse por defecto
df.write.mode("overwrite").format("delta").saveAsTable("dim_customer")
print("Tabla dim_customer escrita")
```

- [ ] **Step 4: Crear `DemoVariables.VariableLibrary/`**

`.platform`:

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
  "metadata": {
    "type": "VariableLibrary",
    "displayName": "DemoVariables",
    "description": "Configuración por entorno de la demo"
  },
  "config": {
    "version": "2.0",
    "logicalId": "aaaaaaaa-0000-4000-8000-000000000002"
  }
}
```

`variables.json` (los valores por defecto son los de **Dev**):

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/variableLibrary/definition/variables/1.0.0/schema.json",
  "variables": [
    {
      "name": "lakehouse_id",
      "note": "GUID de DemoLakehouse en el workspace del entorno",
      "type": "String",
      "value": "00000000-0000-0000-0000-000000000000"
    },
    {
      "name": "workspace_id",
      "note": "GUID del workspace del entorno",
      "type": "String",
      "value": "11111111-1111-1111-1111-111111111111"
    }
  ]
}
```

`valueSets/Prod.json`:

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/variableLibrary/definition/valueSet/1.0.0/schema.json",
  "name": "Prod",
  "overrides": [
    { "name": "lakehouse_id", "value": "22222222-2222-2222-2222-222222222222" },
    { "name": "workspace_id", "value": "33333333-3333-3333-3333-333333333333" }
  ]
}
```

`settings.json`:

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/variableLibrary/definition/settings/1.0.0/schema.json",
  "valueSetsOrder": ["Prod"],
  "activeValueSetName": "Default"
}
```

**Nota de exactitud:** los `$schema` y nombres de campo de la Variable Library deben cotejarse con un export real de Fabric en cuanto exista el workspace de la demo (el formato es reciente y puede variar). El `key_value_replace` de `parameter.yml` apunta a `$.activeValueSetName` de este `settings.json` — si el export real usa otra propiedad, actualizar ambos archivos a la vez.

- [ ] **Step 5: Crear `DemoLakehouse.Lakehouse/.platform`**

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
  "metadata": {
    "type": "Lakehouse",
    "displayName": "DemoLakehouse",
    "description": "Destino de la demo; las tablas las crea el notebook"
  },
  "config": {
    "version": "2.0",
    "logicalId": "aaaaaaaa-0000-4000-8000-000000000003"
  }
}
```

- [ ] **Step 6: Crear `DemoPipeline.DataPipeline/`**

`.platform`:

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
  "metadata": {
    "type": "DataPipeline",
    "displayName": "DemoPipeline",
    "description": "Orquesta DemoNotebook usando variables de DemoVariables"
  },
  "config": {
    "version": "2.0",
    "logicalId": "aaaaaaaa-0000-4000-8000-000000000004"
  }
}
```

`pipeline-content.json` — la actividad referencia el workspace vía la Variable Library (`@pipeline().libraryVariables.DemoVariables.workspace_id`); el `notebookId` queda con el GUID de Dev y se documenta que fabric-cicd lo reescribe si se añade la regla correspondiente, o que el propio Fabric lo reasigna al desplegar por `logicalId`:

```json
{
  "properties": {
    "activities": [
      {
        "name": "Ejecutar DemoNotebook",
        "type": "TridentNotebook",
        "dependsOn": [],
        "policy": {
          "timeout": "0.01:00:00",
          "retry": 0,
          "secureInput": false,
          "secureOutput": false
        },
        "typeProperties": {
          "notebookId": "44444444-4444-4444-4444-444444444444",
          "workspaceId": {
            "value": "@pipeline().libraryVariables.DemoVariables.workspace_id",
            "type": "Expression"
          }
        }
      }
    ]
  }
}
```

- [ ] **Step 7: Verificar JSON**

Run: `python -c "import json,glob; [json.load(open(f, encoding='utf-8')) for f in glob.glob('src/workspace/**/*.json', recursive=True) + glob.glob('src/workspace/**/.platform', recursive=True)]; print('OK')"`
Expected: `OK`

- [ ] **Step 8: Ejecutar validate.py contra la estructura creada**

Run: `pip install pyyaml` (si falta) y `python src/deploy/validate.py`
Expected: `Validación OK`

- [ ] **Step 9: Commit**

```bash
git add src/workspace/
git commit -m "feat: definiciones de referencia de los items de Fabric"
```

---

### Task 4: `docs/01-prerrequisitos.md` y `docs/02-workspaces.md`

**Files:**
- Create: `docs/01-prerrequisitos.md`
- Create: `docs/02-workspaces.md`
- Create: `assets/.gitkeep`

- [ ] **Step 1: Crear `docs/01-prerrequisitos.md`** con esta estructura y contenido (prosa en español alrededor de cada punto):

```markdown
# Módulo 01 — Prerrequisitos

[Intro: qué vas a montar y cuánto se tarda (~2-3 h replicando con calma).]

## Qué necesitas

| Recurso | Detalle | Coste |
| --- | --- | --- |
| Tenant de Microsoft Entra ID | Con permiso para crear app registrations (o que un admin te cree una) | Gratis |
| Capacidad de Microsoft Fabric | Trial de 60 días válido — activar desde app.fabric.microsoft.com | Gratis (trial) |
| Organización de Azure DevOps | dev.azure.com, tier gratuito | Gratis |
| Python 3.10+ local (opcional) | Solo para probar fabric-cicd en local (módulo 06) | Gratis |

## Permisos y tenant settings de Fabric
[Lista: ser admin del tenant o pedirlo. Settings necesarios en el Admin portal:]
- "Users can create Fabric items"
- "Service principals can use Fabric APIs" (imprescindible para el módulo 07)
- Git integration habilitado ("Users can synchronize workspace items with their Git repositories")

## Conocimientos previos
[Git básico (branch, PR, merge). No hace falta experiencia previa con fabric-cicd.]

## ✅ Checkpoint
- [ ] Puedes entrar en app.fabric.microsoft.com y crear un workspace de prueba
- [ ] Tienes una organización de ADO con un proyecto
- [ ] Sabes quién puede tocar los tenant settings si algo falla

## Errores típicos
| Síntoma | Causa | Solución |
| --- | --- | --- |
| "Upgrade to a paid version" al crear ítems | Sin capacidad asignada | Activar el trial de Fabric |
| No aparece la opción de Git en el workspace | Tenant setting de Git deshabilitado | Pedir al admin que lo habilite |

➡️ Siguiente: [Módulo 02 — Workspaces](02-workspaces.md)
```

- [ ] **Step 2: Crear `docs/02-workspaces.md`** con esta estructura:

```markdown
# Módulo 02 — Crear los workspaces

[Intro: dos workspaces, Dev conectado a Git, Prod solo recibe despliegues.]

## Crear "GFD26 - Dev" y "GFD26 - Prod"
[Pasos UI: Workspaces > New workspace; asignar la capacidad (trial) en Advanced.
Captura sugerida: assets/02-new-workspace.png]

## Convención de nombres
[Por qué un prefijo común (GFD26) facilita encontrar los workspaces, y que
el nombre NO viaja en los despliegues: fabric-cicd apunta por GUID.]

## Apunta los GUIDs
[Cómo obtener el GUID de cada workspace desde la URL
(app.fabric.microsoft.com/groups/<GUID>/...). Tabla para rellenar:]

| Workspace | GUID |
| --- | --- |
| GFD26 - Dev | _(pégalo aquí)_ |
| GFD26 - Prod | _(pégalo aquí)_ |

## ✅ Checkpoint
- [ ] Ambos workspaces existen y tienen capacidad asignada (icono de diamante/trial)
- [ ] Tienes los dos GUIDs apuntados

## Errores típicos
[Workspace sin capacidad => los ítems de la demo no se pueden crear.]

⬅️ [Módulo 01](01-prerrequisitos.md) · ➡️ [Módulo 03 — Contenido de la demo](03-contenido-demo.md)
```

- [ ] **Step 3: Crear `assets/.gitkeep`** (archivo vacío; las capturas se añaden al montar la demo real)

- [ ] **Step 4: Verificar enlaces relativos** — todos los `(0X-*.md)` referenciados existen o se crean en tareas 4-7 de este plan; verificar al final de la Task 7.

- [ ] **Step 5: Commit**

```bash
git add docs/01-prerrequisitos.md docs/02-workspaces.md assets/.gitkeep
git commit -m "docs: modulos 01 (prerrequisitos) y 02 (workspaces)"
```

---

### Task 5: `docs/03-contenido-demo.md` y `docs/04-git-integration.md`

**Files:**
- Create: `docs/03-contenido-demo.md`
- Create: `docs/04-git-integration.md`

- [ ] **Step 1: Crear `docs/03-contenido-demo.md`** — el módulo más largo. Estructura:

```markdown
# Módulo 03 — Crear el contenido de la demo

[Intro + diagrama de dependencias: Report -> Model -> Lakehouse <- Notebook <- Pipeline,
con DemoVariables alimentando al Pipeline.]

## 1. DemoLakehouse
[New item > Lakehouse, nombre exacto "DemoLakehouse" (los nombres importan:
parameter.yml referencia $items.Lakehouse.DemoLakehouse.$id). Apuntar su GUID
desde la URL.]

## 2. DemoVariables (Variable Library)
[New item > Variable Library. Crear variables lakehouse_id y workspace_id (String)
con los valores de Dev. Add value set "Prod" con los GUIDs de Prod
(el lakehouse de Prod aún no existe: déjalo con el valor de Dev y
actualízalo tras el primer despliegue, sección final del módulo 08).
Referencia al formato: ../src/workspace/DemoVariables.VariableLibrary/]

## 3. DemoNotebook
[New item > Notebook, adjuntar DemoLakehouse como default lakehouse.
Pegar el código de ../src/workspace/DemoNotebook.Notebook/notebook-content.py
(solo las celdas, no los comentarios META). Ejecutarlo y comprobar que
aparece la tabla dim_customer en el lakehouse.]

## 4. DemoPipeline
[New item > Data pipeline. Actividad Notebook apuntando a DemoNotebook.
En Settings > Workspace, usar la referencia a la variable de librería
(@pipeline().libraryVariables.DemoVariables.workspace_id) — pasos UI del
selector de variable library. Ejecutar el pipeline y verificar.]

## 5. DemoModel (modelo semántico Direct Lake)
[Desde DemoLakehouse > New semantic model, seleccionar dim_customer,
nombre "DemoModel". Añadir 1-2 medidas DAX de ejemplo:
Total Customers = COUNTROWS(dim_customer).]

## 6. DemoReport
[New report sobre DemoModel, una página, 2-3 visuales (tarjeta con
Total Customers + tabla/barras). Guardar como "DemoReport".]

## ✅ Checkpoint
- [ ] La tabla dim_customer existe y tiene filas
- [ ] El pipeline ejecuta el notebook sin errores usando la variable de librería
- [ ] El informe muestra datos

## Errores típicos
[Notebook sin default lakehouse => saveAsTable falla.
Variable library: olvidar Save tras editar => el pipeline lee el valor viejo.]

⬅️ [Módulo 02](02-workspaces.md) · ➡️ [Módulo 04 — Git integration](04-git-integration.md)
```

- [ ] **Step 2: Crear `docs/04-git-integration.md`**. Estructura:

```markdown
# Módulo 04 — Conectar el workspace a Git

## 1. Crear el repo en Azure DevOps
[Proyecto en ADO > Repos > nuevo repo "fabric-cicd-demo" con README inicial.
Crear la rama dev desde main. Copiar a la raíz del repo las carpetas
deploy/ y pipelines/ de este repo de GitHub (src/deploy y src/pipelines).]

## 2. Conectar "GFD26 - Dev" a la rama dev
[Workspace settings > Git integration > Azure DevOps. Org/proyecto/repo/rama dev,
carpeta Git: /workspace. Al conectar, Fabric pide hacer commit inicial:
todos los ítems del módulo 03 se exportan al repo. Captura sugerida:
assets/04-git-connect.png]

## 3. Explora lo que Fabric ha escrito
[Recorrido por el formato: carpetas <Nombre>.<Tipo>, archivo .platform con
logicalId, notebook-content.py, definición de la variable library...
Comparar con ../src/workspace/ de este repo.]

## 4. Flujo branch-out (feature workspaces)
[Workspace Dev > menú de rama (abajo izquierda) > Branch out to new workspace:
Fabric crea rama feature/<nombre> + workspace nuevo sincronizado.
Hacer un cambio pequeño (p. ej. una celda del notebook), commit desde el
workspace feature, y PR feature -> dev en ADO. Tras el merge: en el workspace
Dev, Source control > Update from Git (manual a propósito en la demo;
automatizable vía API, fuera de alcance).]

## 5. Políticas de rama en main
[Repos > Branches > main > Branch policies: mínimo 1 reviewer +
build validation con pipelines/azure-pipelines-ci.yml (se crea el pipeline
en el módulo 07; volver aquí para activar la policy).]

## ✅ Checkpoint
- [ ] El repo ADO tiene /workspace con todos los ítems tras el commit inicial
- [ ] Un cambio hecho vía branch-out ha llegado a dev por PR y el workspace
      Dev lo muestra tras Update from Git

## Errores típicos
[Carpeta Git equivocada al conectar => Fabric mezcla ítems con deploy/.
Update from Git no aparece => no hay cambios nuevos en la rama.]

⬅️ [Módulo 03](03-contenido-demo.md) · ➡️ [Módulo 05 — Service principal](05-service-principal.md)
```

- [ ] **Step 3: Commit**

```bash
git add docs/03-contenido-demo.md docs/04-git-integration.md
git commit -m "docs: modulos 03 (contenido demo) y 04 (git integration)"
```

---

### Task 6: `docs/05-service-principal.md` y `docs/06-fabric-cicd.md`

**Files:**
- Create: `docs/05-service-principal.md`
- Create: `docs/06-fabric-cicd.md`

- [ ] **Step 1: Crear `docs/05-service-principal.md`**. Estructura:

```markdown
# Módulo 05 — Service principal

[Intro: el pipeline no puede usar tu usuario; necesita una identidad propia.]

## 1. Crear la app registration
[Entra ID > App registrations > New. Sin permisos de API delegados:
fabric-cicd usa el rol de workspace, no permisos de Graph.]

## 2. Variante A — Secreto de cliente
[Certificates & secrets > New client secret. Apuntar: tenant ID, client ID,
secreto (solo visible una vez). Más simple; el secreto caduca y hay que rotarlo.]

## 3. Variante B — Federación (Workload Identity)
[En ADO: Project settings > Service connections > New > Azure Resource Manager
> Workload Identity federation (automatic), nombre "sc-fabric-cicd-demo".
ADO crea la app o federa una existente; sin secretos que rotar.
Recomendada para uso real.]

## 4. Dar acceso al workspace Prod
[GFD26 - Prod > Manage access > Add people or groups > buscar la app por
nombre > rol Admin (Member basta para publicar, Admin evita fricciones
en la demo).]

## 5. Tenant setting
["Service principals can use Fabric APIs" habilitado (Admin portal),
idealmente acotado a un grupo de seguridad que contenga el SP.]

## ✅ Checkpoint
- [ ] Tienes tenant ID + client ID (+ secreto, variante A) apuntados
- [ ] El SP aparece en Manage access del workspace Prod
- [ ] El tenant setting está activo

## Errores típicos
| Síntoma | Causa | Solución |
| --- | --- | --- |
| 401 al desplegar | Tenant setting de SPs deshabilitado | Habilitarlo (tarda ~15 min en propagar) |
| 403 / workspace not found | SP sin rol en el workspace | Añadirlo como Admin/Member |

⬅️ [Módulo 04](04-git-integration.md) · ➡️ [Módulo 06 — fabric-cicd](06-fabric-cicd.md)
```

- [ ] **Step 2: Crear `docs/06-fabric-cicd.md`**. Estructura:

```markdown
# Módulo 06 — La librería fabric-cicd

## ¿Qué es?
[Librería Python open source de Microsoft para publicar ítems de Fabric desde
un repo Git: lee las definiciones, aplica parameter.yml y llama a las APIs.
Enlaces: https://microsoft.github.io/fabric-cicd/ y PyPI.]

## deploy.py por dentro
[Recorrido comentado del script (../src/deploy/deploy.py): FabricWorkspace,
publish_all_items, unpublish_all_orphan_items — y la advertencia de que
unpublish borra ítems del workspace que ya no están en la rama.]

## parameter.yml: el corazón de la promoción
[Recorrido de ../src/workspace/parameter.yml:
1. key_value_replace activa el value set Prod de DemoVariables ($.activeValueSetName).
2. find_replace con tokens dinámicos ($items.Lakehouse.DemoLakehouse.$id,
   $workspace.$id) para los GUIDs incrustados (conexión Direct Lake del modelo).
Mensaje clave: "Variable Library para lo que el runtime resuelve;
parameter.yml para lo que va incrustado en las definiciones."]

## Sustituir los GUIDs de ejemplo
[Tabla de marcadores a sustituir en parameter.yml y dónde encontrar cada GUID real:]
| Marcador | Sustituir por |
| --- | --- |
| 00000000-... | GUID de DemoLakehouse en Dev (URL del lakehouse) |
| 11111111-... | GUID del workspace Dev |

## Probar en local antes del pipeline
[Con Azure CLI logueado (az login):
pip install -r deploy/requirements.txt
python deploy/deploy.py --workspace-id <GUID-Prod> --environment PROD --auth cli
Esto despliega TODO a Prod desde tu máquina — útil para validar antes de
montar el pipeline. Salida esperada: lista de ítems publicados.]

## ✅ Checkpoint
- [ ] parameter.yml tiene los GUIDs reales de tu Dev
- [ ] El despliegue local a Prod termina sin errores y los ítems aparecen en GFD26 - Prod

## Errores típicos
[parameter.yml no encontrado => debe estar en la carpeta workspace/ (repository_directory).
Item type not in scope => revisar ITEM_TYPES en deploy.py.]

⬅️ [Módulo 05](05-service-principal.md) · ➡️ [Módulo 07 — Pipelines](07-pipelines-ado.md)
```

- [ ] **Step 3: Commit**

```bash
git add docs/05-service-principal.md docs/06-fabric-cicd.md
git commit -m "docs: modulos 05 (service principal) y 06 (fabric-cicd)"
```

---

### Task 7: `docs/07-pipelines-ado.md` y `docs/08-flujo-completo.md`

**Files:**
- Create: `docs/07-pipelines-ado.md`
- Create: `docs/08-flujo-completo.md`

- [ ] **Step 1: Crear `docs/07-pipelines-ado.md`**. Estructura:

```markdown
# Módulo 07 — Pipelines de Azure DevOps

## 1. Variable group
[Pipelines > Library > Variable group "fabric-cicd-demo" con:
PROD_WORKSPACE_ID, y para la variante A: AZURE_TENANT_ID, AZURE_CLIENT_ID,
AZURE_CLIENT_SECRET (candado = secreta).]

## 2. Environment con aprobación
[Pipelines > Environments > New "fabric-prod" > Approvals and checks >
Approvals > añadirte como aprobador. Esto pausa el CD hasta aprobar.]

## 3. Crear los dos pipelines
[Pipelines > New pipeline > Azure Repos Git > Existing YAML:
- pipelines/azure-pipelines-ci.yml (nombrarlo "CI - validacion")
- pipelines/azure-pipelines-cd.yml (nombrarlo "CD - deploy prod")
Primer run del CD: autorizar el variable group y el environment cuando
ADO lo pida.]

## 4. Activar la build validation en main
[Volver al módulo 04 §5: Branch policies de main > Build validation >
seleccionar "CI - validacion".]

## 5. Las dos variantes de auth en el YAML
[Explicar el parámetro authMode (secret | federated) del CD y cuándo usar
cada una; la federada requiere la service connection del módulo 05 §3.]

## ✅ Checkpoint
- [ ] Un PR de prueba hacia main ejecuta el CI automáticamente
- [ ] El CD aparece en Pipelines y tiene acceso al variable group y al environment

## Errores típicos
[Pipeline "could not access variable group" => autorizar el recurso.
El CD no se dispara => revisar el path filter (workspace/**, deploy/**).]

⬅️ [Módulo 06](06-fabric-cicd.md) · ➡️ [Módulo 08 — Flujo completo](08-flujo-completo.md)
```

- [ ] **Step 2: Crear `docs/08-flujo-completo.md`** — el guion de la demo. Estructura:

```markdown
# Módulo 08 — El flujo completo (guion de la demo)

[Intro: ya está todo montado; este es el recorrido end-to-end que se enseña
en la charla, paso a paso con lo que el público ve en cada momento.]

## El recorrido

1. **Branch out**: desde GFD26 - Dev, crear feature/demo-gfd y su workspace.
2. **Cambio visible**: editar DemoNotebook (p. ej. añadir una columna calculada
   al dataframe) o una medida del modelo. Commit desde el workspace feature.
3. **PR feature -> dev** en ADO. Merge.
4. **Update from Git** en GFD26 - Dev: el cambio aparece en Dev.
5. **PR dev -> main**: el CI de validación se ejecuta como build validation.
   Merge.
6. **El CD se dispara**: stage DeployProd queda **esperando aprobación**
   en el environment fabric-prod. [Momento de la charla: enseñar el correo/
   pantalla de aprobación.] Aprobar.
7. **fabric-cicd publica en Prod**: revisar el log del pipeline (ítems
   publicados, value set Prod activado, GUIDs reescritos).
8. **Verificar en Prod**: abrir GFD26 - Prod, ejecutar DemoPipeline
   (o comprobar el informe) y ver el cambio.

## Primera ejecución: cerrar el círculo de la Variable Library
[Tras el PRIMER despliegue a Prod, DemoLakehouse ya existe en Prod:
copiar su GUID y el del workspace Prod al value set Prod de DemoVariables
(en Dev), commit, PR dev -> main de nuevo. A partir de ahí el value set
Prod tiene valores reales. Nota: el find_replace con $items.... evita
este paso para los GUIDs incrustados; el value set cubre lo que el
pipeline resuelve en runtime.]

## ✅ Checkpoint final
- [ ] Un cambio nacido en una rama feature es visible en el informe de Prod
      tras aprobar el pipeline
- [ ] Nadie ha tocado el workspace Prod a mano

## Si algo falla en directo (plan B)
[Tabla rápida: CI rojo => leer el error de validate.py; CD no dispara =>
path filter; 401/403 => módulo 05; ítem no aparece en Prod => revisar
ITEM_TYPES y el log de publish_all_items.]

⬅️ [Módulo 07](07-pipelines-ado.md) · 🏠 [Inicio](../README.md)
```

- [ ] **Step 3: Verificar todos los enlaces relativos de docs/** — cada `(<archivo>.md)` y `(../src/...)` referenciado existe.

Run: `grep -roh "](\.\./[^)]*\|]([0-9][^)]*" docs/*.md | sort -u` y comprobar cada ruta con `ls`.

- [ ] **Step 4: Commit**

```bash
git add docs/07-pipelines-ado.md docs/08-flujo-completo.md
git commit -m "docs: modulos 07 (pipelines ADO) y 08 (flujo completo)"
```

---

### Task 8: `README.md` (portada)

**Files:**
- Create: `README.md`

- [ ] **Step 1: Crear `README.md`**. Estructura:

```markdown
# CI/CD en Microsoft Fabric — Global Fabric Day 2026 (Alicante)

[1-2 frases: repo de la charla; contiene la guía para replicar la demo
completa y todo el contenido (script de despliegue, pipelines, definiciones).]

## El flujo que vas a montar

```
feature/* (branch-out desde Fabric)
    │  PR a dev
    ▼
dev ──Git integration──▶ Workspace Dev
    │
    │  PR de dev a main ──▶ merge dispara el pipeline CD
    ▼
main ──▶ fabric-cicd ──▶ Workspace Prod  (con aprobación manual)
```

## La guía
| # | Módulo | Qué haces |
| --- | --- | --- |
| 01 | [Prerrequisitos](docs/01-prerrequisitos.md) | Cuentas, capacidad, permisos |
| 02 | [Workspaces](docs/02-workspaces.md) | Crear Dev y Prod |
| 03 | [Contenido de la demo](docs/03-contenido-demo.md) | Lakehouse, Variable Library, notebook, pipeline, modelo, informe |
| 04 | [Git integration](docs/04-git-integration.md) | Conectar Dev a ADO, branch-out |
| 05 | [Service principal](docs/05-service-principal.md) | Identidad del pipeline (2 variantes) |
| 06 | [fabric-cicd](docs/06-fabric-cicd.md) | deploy.py, parameter.yml, prueba local |
| 07 | [Pipelines de ADO](docs/07-pipelines-ado.md) | CI + CD con aprobación |
| 08 | [Flujo completo](docs/08-flujo-completo.md) | El guion de la demo end-to-end |

## Qué hay en el repo
[Tabla src/workspace, src/deploy, src/pipelines con una línea cada uno.]

## ¿Cuánto cuesta replicarlo?
[Nada: trial de Fabric (60 días) + tier gratuito de Azure DevOps.]

## Recursos
[Enlaces: docs de fabric-cicd (microsoft.github.io/fabric-cicd), tutorial
oficial ADO+fabric-cicd en Learn, docs de Variable Libraries, este spec.]
```

- [ ] **Step 2: Verificar enlaces del README**

Run: `ls docs/0*.md src/deploy src/pipelines src/workspace`
Expected: existen todos los referenciados.

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: README portada con diagrama e indice de la guia"
```

---

### Task 9: Revisión final de coherencia

- [ ] **Step 1: Revisión cruzada de nombres y valores** — comprobar que estos literales son idénticos en todos los archivos donde aparecen:
  - `DemoVariables`, `DemoLakehouse`, `DemoNotebook`, `DemoPipeline`, `DemoModel`, `DemoReport`
  - `GFD26 - Dev`, `GFD26 - Prod`, `fabric-cicd-demo` (variable group), `fabric-prod` (environment), `sc-fabric-cicd-demo` (service connection), `PROD` (entorno)
  - Marcadores GUID `00000000-...` (lakehouse Dev) y `11111111-...` (workspace Dev) coinciden entre `parameter.yml`, `notebook-content.py` y `variables.json`

Run: `grep -rn "DemoVariables\|fabric-prod\|sc-fabric-cicd-demo\|fabric-cicd-demo" --include="*.md" --include="*.yml" --include="*.py" --include="*.json" .` y revisar incoherencias.

- [ ] **Step 2: Corregir lo que aparezca y commit final**

```bash
git add -A
git commit -m "chore: revision final de coherencia de nombres y enlaces"
```
