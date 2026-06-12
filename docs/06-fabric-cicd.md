# Módulo 06 — La librería fabric-cicd

## ¿Qué es?

`fabric-cicd` es una **librería Python de código abierto mantenida por Microsoft** que automatiza la publicación de ítems de Fabric desde un repositorio Git. Su flujo es sencillo: lee las definiciones de ítems que hay en una carpeta del repo, aplica las sustituciones declaradas en `parameter.yml` (cambios de GUIDs, activación de value sets, etc.) y llama a las APIs REST de Fabric para crear o actualizar los ítems en el workspace destino.

- Documentación oficial: <https://microsoft.github.io/fabric-cicd/>
- Paquete en PyPI: `fabric-cicd`

## deploy-to-fabric.py por dentro

El script `deploy/deploy-to-fabric.py` es el punto de entrada del pipeline. Aquí tienes un recorrido comentado de lo que hace:

```python
from fabric_cicd import FabricWorkspace, publish_all_items, unpublish_all_orphan_items
```

Importa las tres piezas clave de la librería:

- **`FabricWorkspace`** — objeto que representa el workspace destino. Recibe el GUID del workspace, el nombre del entorno (p. ej. `"pro"`), la carpeta con las definiciones, la lista de tipos de ítem en alcance y la credencial de autenticación.
- **`publish_all_items`** — publica (crea o actualiza) todos los ítems del repo cuyo tipo esté en `ITEM_TYPES`.
- **`unpublish_all_orphan_items`** — **borra del workspace** los ítems que ya no existen en la rama. Úsalo con precaución en Pro: si retiras un ítem del repo, esta función lo eliminará del workspace en el siguiente despliegue.

Los tipos de ítem que el script pone en alcance son:

```python
ITEM_TYPES = [
    "Lakehouse",
    "VariableLibrary",
    "Notebook",
    "DataPipeline",
    "SemanticModel",
    "Report",
]
```

Solo se publican ítems cuyo tipo esté en esta lista; el resto se ignora aunque exista en la carpeta del repo.

El script acepta los siguientes argumentos:

| Argumento | Descripción |
| --- | --- |
| `--aztenantid` | GUID del tenant de Azure AD |
| `--azclientid` | Client ID del Service Principal |
| `--azspsecret` | Client Secret del Service Principal |
| `--items_in_scope` | Lista JSON de tipos de ítem a publicar |
| `--target_env` | Nombre del entorno destino (p. ej. `pro`) |

Además de los argumentos, el script lee dos variables de entorno con `os.environ`:

| Variable | Valor esperado | Descripción |
| --- | --- | --- |
| `PROWORKSPACENAME` | `GFD_PRO` | Nombre del workspace de producción |
| `GITDIRECTORY` | `fabric` | Carpeta Git donde Fabric guardó las definiciones |

## parameter.yml: el corazón de la promoción

El archivo `fabric/parameter.yml` define **qué cambia entre entornos**. Tiene dos secciones:

### find_replace

La sección `find_replace` busca GUIDs concretos en **todos** los archivos de definición del repo y los sustituye por referencias dinámicas que fabric-cicd resuelve consultando el workspace destino en tiempo de ejecución.

```yaml
find_replace:
  - find_value: "6b2d8c5d-8eb6-4b89-8f9e-5cfc82bdf2bb"
    replace_value:
      pro: "$workspace.$id"
  - find_value: "1546a512-5301-4200-a7e8-774ac7cba230"
    replace_value:
      pro: "$items.Lakehouse.LH_GlobalFabricDay.$id"
```

¿Por qué aparecen estos GUIDs en el repo? Los notebooks `NB_LoadTalks_Pipeline` y `NB_ProcessTalks_Pipeline` tienen el lakehouse `LH_GlobalFabricDay` **vinculado como lakehouse por defecto**. Esa vinculación queda incrustada por GUID en los metadatos del notebook — no puede resolverse con variables en runtime. Del mismo modo, el GUID del workspace `GFD_DEV` aparece en las referencias de workspace dentro de las definiciones de los ítems. Tener estos GUIDs en el repo es completamente deliberado: son exactamente los valores que fabric-cicd necesita localizar para sustituirlos por los del entorno destino al desplegar.

> **Mensaje clave:** el value set `pro` en el repo lleva los GUIDs de dev como placeholder; fabric-cicd los sustituye por los del workspace destino al desplegar — no hay que tocarlos a mano.

### key_value_replace

La sección `key_value_replace` modifica valores concretos dentro de las definiciones JSON de los ítems mediante expresiones JSONPath. Se usa para actualizar referencias entre ítems (como el `notebookId` en las actividades del pipeline) y para activar el value set correcto en la Variable Library:

```yaml
key_value_replace:
  - find_key: "$.activities[?(@.name=='LoadTalks')].typeProperties.notebookId"
    replace_value:
      pro: "$items.Notebook.NB_LoadTalks_Pipeline.$id"
    item_type: "DataPipeline"
    item_name: "PL_Orquestador"
  - find_key: "$.activities[?(@.name=='ProcessTalks')].typeProperties.notebookId"
    replace_value:
      pro: "$items.Notebook.NB_ProcessTalks_Pipeline.$id"
    item_type: "DataPipeline"
    item_name: "PL_Orquestador"
  - find_key: "$.activities[?(@.name=='LoadTalks')].typeProperties.workspaceId"
    replace_value:
      pro: "$workspace.$id"
    item_type: "DataPipeline"
    item_name: "PL_Orquestador"
  - find_key: "$.activities[?(@.name=='ProcessTalks')].typeProperties.workspaceId"
    replace_value:
      pro: "$workspace.$id"
    item_type: "DataPipeline"
    item_name: "PL_Orquestador"
  - find_key: "$.valuesets[?(@.name=='pro')].values[?(@.name=='WORKSPACE_ID')].value"
    replace_value:
      pro: "$workspace.$id"
    item_type: "VariableLibrary"
    item_name: "VL_GlobalFabricDay"
  - find_key: "$.valuesets[?(@.name=='pro')].values[?(@.name=='LAKEHOUSE_ID')].value"
    replace_value:
      pro: "$items.Lakehouse.LH_GlobalFabricDay.$id"
    item_type: "VariableLibrary"
    item_name: "VL_GlobalFabricDay"
```

Las reglas de `key_value_replace` para `PL_Orquestador` actualizan los `notebookId` y `workspaceId` de las actividades `LoadTalks` y `ProcessTalks` con los IDs reales del entorno destino. Las dos últimas reglas actúan sobre la Variable Library `VL_GlobalFabricDay`: sustituyen los valores de `WORKSPACE_ID` y `LAKEHOUSE_ID` en el value set `pro`.

> **Mensaje clave:** usa la Variable Library para lo que el runtime puede resolver; usa `parameter.yml` para lo que va incrustado en las definiciones de los ítems.

## Probar en local antes del pipeline

Puedes desplegar directamente a `GFD_PRO` desde tu máquina para validar la configuración antes de montar el pipeline. El script usa un Service Principal, así que necesitas tener las credenciales a mano.

### 1. Exportar las variables de entorno

```powershell
$env:PROWORKSPACENAME = "GFD_PRO"
$env:GITDIRECTORY = "fabric"
```

### 2. Ejecutar el script

```bash
pip install fabric-cicd
python deploy/deploy-to-fabric.py \
  --aztenantid <tenant-id> \
  --azclientid <client-id> \
  --azspsecret <secret> \
  --items_in_scope '["Lakehouse","VariableLibrary","Notebook","DataPipeline","SemanticModel","Report"]' \
  --target_env pro
```

El resultado esperado es una lista de los ítems publicados en `GFD_PRO`. Si algo falla, el error de la API suele indicar claramente qué ítem o qué permiso falta.

> **Aviso:** el script usa el Service Principal, no tu sesión personal. Asegúrate de que el SP tiene rol **Contributor** (o superior) en el workspace `GFD_PRO` antes de hacer esta prueba.

## Checkpoint

- [ ] Las variables `PROWORKSPACENAME` y `GITDIRECTORY` están exportadas en la sesión de PowerShell
- [ ] El despliegue local a `GFD_PRO` termina sin errores y los ítems aparecen en el workspace
- [ ] `parameter.yml` tiene las reglas `find_replace` con los GUIDs de `GFD_DEV` y `LH_GlobalFabricDay`
- [ ] `parameter.yml` tiene las reglas `key_value_replace` para `PL_Orquestador` y `VL_GlobalFabricDay` con el entorno `pro`

## Errores típicos

| Síntoma | Causa | Solución |
| --- | --- | --- |
| `parameter.yml` no encontrado | La carpeta `fabric/` no es el directorio configurado | Verificar que `GITDIRECTORY=fabric` está exportado antes de ejecutar el script |
| `Item type not in scope` | El tipo de ítem no está en `--items_in_scope` | Añadir el tipo correspondiente a la lista del argumento |
| Error de GUID incrustado tras desplegar | Las reglas `find_replace` no cubren todos los GUIDs de dev | Revisar los metadatos del ítem afectado y añadir la regla correspondiente en `parameter.yml` |
| `PROWORKSPACENAME` no definida | La variable de entorno no está exportada | Exportar con `$env:PROWORKSPACENAME = "GFD_PRO"` antes de ejecutar el script |

⬅️ [Módulo 05](05-service-principal.md) · ➡️ [Módulo 07 — Pipelines](07-pipelines-ado.md)
