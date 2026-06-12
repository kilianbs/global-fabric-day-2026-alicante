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
