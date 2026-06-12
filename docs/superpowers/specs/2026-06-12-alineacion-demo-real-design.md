# Diseño: Alineación del repo con la demo real — Global Fabric Day 2026 Alicante

**Fecha:** 2026-06-12
**Estado:** Aprobado
**Sustituye parcialmente a:** `2026-06-11-fabric-cicd-demo-repo-design.md` (la estructura general sigue vigente; este spec actualiza nomenclatura, flujo de ramas, autenticación y los pipelines de despliegue).

## Objetivo

Alinear la guía (`docs/`), la portada (`README.md`) y el contenido replicable (`src/`) con la demo real ya construida en Fabric y Azure DevOps. El contenido de `src/workspace/` ya es el export real del workspace de desarrollo; el trabajo es de coherencia: nombres, ramas, rutas, parameter.yml, pipelines y reescritura de los módulos afectados.

## Decisiones clave

| Decisión | Elección |
|---|---|
| Workspaces | **GFD_DEV** (desarrollo, git-sync) y **GFD_PRO** (producción, solo despliegues) |
| Repo de ADO | **Global Fabric Day** |
| Ramas | Solo `dev` (rama por defecto, conectada a GFD_DEV) y `pro` (despliega a GFD_PRO). **No existe `main`** |
| Carpeta Git en Fabric | `fabric` |
| Entorno de despliegue | Único: `pro`. Los pipelines disparan solo en la rama `pro` |
| Autenticación | Solo SP con secreto. **Desaparece la Variante B (Workload Identity Federation)** |
| Caminos de despliegue | Tres: completo, solo cambios, selectivo manual |
| Réplica en GitHub | `src/` espeja 1:1 el repo de ADO: `src/fabric/`, `src/deploy/`, `src/pipelines/` |

## Nomenclatura de artefactos

Prefijo por tipo + `GlobalFabricDay`, salvo los notebooks que tienen nombre funcional:

| Artefacto | Tipo |
|---|---|
| `LH_GlobalFabricDay` | Lakehouse |
| `VL_GlobalFabricDay` | Variable Library |
| `PL_Orquestador` | Data Pipeline |
| `SM_GlobalFabricDay` | Semantic Model |
| `RPT_GlobalFabricDay` | Report |
| `NB_SetDefaultLakehouse` | Notebook utilitario: `%%configure` con variables de la VL |
| `NB_LoadTalks`, `NB_ProcessTalks` | Notebooks camino 1 (`%run NB_SetDefaultLakehouse`) |
| `NB_LoadTalks_Pipeline`, `NB_ProcessTalks_Pipeline` | Notebooks camino 2 (lakehouse vinculado + parámetros desde pipeline) |
| `NB_Orquestador` | Notebook orquestador |

Desaparecen todas las menciones a `Demo*` (DemoNotebook, DemoVariables, DemoLakehouse...) y a `GFD26*`.

## Variable Library

`VL_GlobalFabricDay` con variables `LAKEHOUSE_ID`, `WORKSPACE_ID`, `LAKEHOUSE_NAME`, `FABRIC_ENV` y un único value set adicional `pro` (el default actúa como dev). Ya está así en `src`; la guía debe describirlo exactamente igual.

## Los dos caminos de buenas prácticas (mensaje central del módulo 03)

1. **Lakehouse en runtime:** `NB_LoadTalks` y `NB_ProcessTalks` empiezan con `%run NB_SetDefaultLakehouse`, que vincula el lakehouse por defecto vía `%%configure` leyendo `LAKEHOUSE_NAME`, `LAKEHOUSE_ID` y `WORKSPACE_ID` de la VL. Cero IDs hardcodeados; nada que reemplazar al desplegar.
2. **Parámetros desde pipeline:** `NB_LoadTalks_Pipeline` y `NB_ProcessTalks_Pipeline` tienen el lakehouse **vinculado** en sus metadatos y reciben parámetros desde `PL_Orquestador`, que a su vez resuelve los valores con la VL (`@pipeline().libraryVariables...`). El lakehouse vinculado (GUIDs en `# META`) es precisamente lo que demuestra el reemplazo de `parameter.yml` durante el despliegue entre entornos.

## Reestructura de `src/`

- Renombrar `src/workspace/` → **`src/fabric/`**. `parameter.yml` permanece dentro (fabric-cicd lo espera en `repository_directory`).
- Borrar: `src/deploy/deploy.py`, `src/deploy/validate.py`, `src/deploy/__pycache__/`, `src/pipelines/azure-pipelines-ci.yml`, `src/pipelines/azure-pipelines-cd.yml`.
- Quedan: `deploy-to-fabric.py/.yml`, `deploy-to-fabric-changes.py/.yml`, `deploy-to-fabric-selective.py` + `deploy-to-fabric-selected-items.yml`, `requirements.txt`.
- Reescribir `src/fabric/README.md`: tabla real de ítems, los dos caminos, rol de `parameter.yml`.

## `parameter.yml` (entorno único `pro`)

- Las claves de entorno pasan de `pre`/`main` a solo `pro`.
- `find_value` con los GUIDs reales de dev presentes en el repo: workspace `6b2d8c5d-8eb6-4b89-8f9e-5cfc82bdf2bb`, lakehouse `1546a512-5301-4200-a7e8-774ac7cba230`.
- Bloque de Variable Library: solo `valueSets/pro.json` (se eliminan las entradas de `pre.json` y `main.json`, que no existen).
- Se mantienen los `key_value_replace` de `notebookId` (LoadTalks, ProcessTalks) y `workspaceId` del DataPipeline.

## Pipelines YAML (3 caminos)

Cambios comunes a los tres: un único stage "Deploy to PRO", entorno/secretos `pro` (`pro-aztenantid`, `pro-azclientid`, `pro-azspsecret`), `scriptPath` corregido de `.deploy/` a `deploy/`, `target_env pro`.

1. **`deploy-to-fabric.yml` (deploy de todo, pipeline por defecto):** trigger en rama `pro` con path `fabric/**`; despliega todos los tipos de ítems.
2. **`deploy-to-fabric-changes.yml` (deploy changes):** mismo trigger; despliega solo los ítems cambiados respecto al último commit (`git diff HEAD~1`); parámetro `force_full_deploy` para forzar despliegue completo.
3. **`deploy-to-fabric-selected-items.yml` (deploy selectivo):** `trigger: none`, ejecución manual; parámetro `items_to_deploy` con ítems separados por comas (default: un ítem real, p. ej. `NB_SetDefaultLakehouse.Notebook`); sin selector de entorno, siempre `pro`.

Los scripts Python se mantienen casi intactos: ya usan la convención de variable groups `{ENV}WORKSPACENAME` (→ `PROWORKSPACENAME=GFD_PRO`) y `GITDIRECTORY` (→ `fabric`).

## Reescritura de docs

| Módulo | Cambio |
|---|---|
| `README.md` | Diagrama y estructura actualizados: GFD_DEV/GFD_PRO, ramas dev/pro, src/fabric |
| 02-workspaces | GFD_DEV y GFD_PRO en todo el texto |
| 03-contenido-demo | Ítems reales; VL con las 4 variables + value set `pro`; los dos caminos de buenas prácticas; lakehouse vinculado como demostración del reemplazo en despliegue |
| 04-git-integration | Repo "Global Fabric Day"; crear ramas `dev` y `pro` sin `main` (`dev` como default); carpeta Git `fabric`; **nueva sección tras el sync**: clonar el repo con VS Code, crear `deploy/` y `pipelines/` con su contenido y `parameter.yml` dentro de `fabric/`, commit y push; políticas de rama sobre `pro` |
| 05-service-principal | Eliminar Variante B (Workload Identity Federation); queda solo SP con secreto |
| 06-fabric-cicd | Rutas `fabric/` y `deploy/`, entorno `pro`, prueba local alineada |
| 07-pipelines-ado | Reescritura alrededor de los 3 caminos con tabla de cuándo usar cada uno; variable groups (`fabric_cicd_group_sensitive` con secretos, `fabric_cicd_group_non_sensitive` con `PROWORKSPACENAME` y `GITDIRECTORY`); registrar `deploy-to-fabric.yml` como pipeline por defecto; sin CI de validación |
| 08-flujo-completo | Recorrido: cambio en GFD_DEV → commit a `dev` → PR `dev`→`pro` → pipeline → aprobar → verificar en GFD_PRO; paso de actualizar GUIDs del value set `pro` tras el primer despliegue |

## Fuera de alcance

- Cambios funcionales en los notebooks o el pipeline de Fabric (ya son el export real).
- Workload Identity Federation (eliminada de la guía).
- Entorno intermedio (pre/test).

## Verificación

- `grep` sin resultados para `GFD26`, `Demo[A-Z]`, `main` como rama de despliegue, `Workload Identity`, `.deploy/`, `pre.json`/`main.json` en docs y src.
- Los `find_value` de `parameter.yml` coinciden con los GUIDs presentes en `src/fabric/`.
- Los tres YAML referencian rutas y scripts existentes.
- Los enlaces internos entre módulos siguen funcionando tras el renombrado de `src/workspace` → `src/fabric`.
