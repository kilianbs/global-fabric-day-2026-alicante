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
