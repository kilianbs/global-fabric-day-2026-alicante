# Módulo 06 — La librería fabric-cicd

## ¿Qué es?

`fabric-cicd` es una **librería Python de código abierto mantenida por Microsoft** que automatiza la publicación de ítems de Fabric desde un repositorio Git. Su flujo es sencillo: lee las definiciones de ítems que hay en una carpeta del repo, aplica las sustituciones declaradas en `parameter.yml` (cambios de GUIDs, activación de value sets, etc.) y llama a las APIs REST de Fabric para crear o actualizar los ítems en el workspace destino.

- Documentación oficial: <https://microsoft.github.io/fabric-cicd/>
- Paquete en PyPI: `fabric-cicd`

## deploy.py por dentro

El script `src/deploy/deploy.py` es el punto de entrada del pipeline. Aquí tienes un recorrido comentado de lo que hace:

```python
from fabric_cicd import FabricWorkspace, publish_all_items, unpublish_all_orphan_items
```

Importa las tres piezas clave de la librería:

- **`FabricWorkspace`** — objeto que representa el workspace destino. Recibe el GUID del workspace, el nombre del entorno (p. ej. `"PROD"`), la carpeta con las definiciones, la lista de tipos de ítem en alcance y la credencial de autenticación.
- **`publish_all_items`** — publica (crea o actualiza) todos los ítems del repo cuyo tipo esté en `ITEM_TYPES`.
- **`unpublish_all_orphan_items`** — **borra del workspace** los ítems que ya no existen en la rama. Úsalo con precaución en Prod: si retiras un ítem del repo, esta función lo eliminará del workspace en el siguiente despliegue.

Los tipos de ítem que el script pone en alcance son:

```python
ITEM_TYPES = [
    "VariableLibrary",
    "Lakehouse",
    "Notebook",
    "DataPipeline",
    "SemanticModel",
    "Report",
]
```

Solo se publican ítems cuyo tipo esté en esta lista; el resto se ignora aunque exista en la carpeta del repo.

El script acepta tres argumentos obligatorios/opcionales:

| Argumento | Obligatorio | Descripción |
| --- | --- | --- |
| `--workspace-id` | Sí | GUID del workspace destino |
| `--environment` | Sí | Nombre del entorno, p. ej. `PROD` |
| `--auth` | No (default: `secret`) | `secret` (client secret) o `cli` (Azure CLI) |

Cuando `--auth secret`, el script espera las variables de entorno `AZURE_TENANT_ID`, `AZURE_CLIENT_ID` y `AZURE_CLIENT_SECRET`. Cuando `--auth cli`, usa la sesión activa de Azure CLI — útil tanto para pruebas locales como para la tarea `AzureCLI@2` del pipeline.

## parameter.yml: el corazón de la promoción

El archivo `src/workspace/parameter.yml` define **qué cambia entre entornos**. Tiene dos secciones:

### key_value_replace

```yaml
key_value_replace:
  - find_key: $.activeValueSetName
    replace_value:
      PROD: "Prod"
    item_type: "VariableLibrary"
    item_name: "DemoVariables"
```

Cuando el entorno destino es `PROD`, fabric-cicd localiza el ítem `DemoVariables` de tipo `VariableLibrary` y sustituye el valor de `$.activeValueSetName` por `"Prod"`. Así la Variable Library activa el value set correcto en producción sin que tengas que editar ningún archivo manualmente.

### find_replace

```yaml
find_replace:
  - find_value: "00000000-0000-0000-0000-000000000000"
    replace_value:
      PROD: "$items.Lakehouse.DemoLakehouse.$id"
  - find_value: "11111111-1111-1111-1111-111111111111"
    replace_value:
      PROD: "$workspace.$id"
```

La conexión Direct Lake del modelo semántico va **incrustada por GUID** en la definición del ítem — no puede resolverse con variables en runtime. Por eso `find_replace` busca los GUIDs de Dev en todos los archivos de definición y los sustituye por los del entorno destino antes de publicar.

Los tokens `$items.Lakehouse.DemoLakehouse.$id` y `$workspace.$id` son referencias dinámicas que fabric-cicd resuelve en tiempo de ejecución consultando el workspace destino.

> **Mensaje clave:** usa la Variable Library para lo que el runtime puede resolver; usa `parameter.yml` para lo que va incrustado en las definiciones de los ítems.

## Sustituir los GUIDs de ejemplo

El `parameter.yml` del repo usa GUIDs de marcador. Antes de desplegar, sustitúyelos por los GUIDs reales de tu entorno Dev:

| Marcador | Sustituir por |
| --- | --- |
| `00000000-0000-0000-0000-000000000000` | GUID de `DemoLakehouse` en Dev (cópialo de la URL del lakehouse en Fabric) |
| `11111111-1111-1111-1111-111111111111` | GUID del workspace `GFD26 - Dev` (cópialo de la URL del workspace) |

Los GUIDs aparecen en la URL cuando navegas al ítem correspondiente en `app.fabric.microsoft.com`.

> Nota: el `notebookId` que verás en la definición de `DemoPipeline` no necesita regla en `parameter.yml` — fabric-cicd resuelve las referencias entre ítems del mismo despliegue automáticamente al publicar.

## Probar en local antes del pipeline

Con Azure CLI instalado e iniciada sesión (`az login`), puedes desplegar directamente a Prod desde tu máquina para validar la configuración antes de montar el pipeline:

```bash
pip install -r src/deploy/requirements.txt
python src/deploy/deploy.py --workspace-id <GUID-Prod> --environment PROD --auth cli
```

Esto despliega **todos** los ítems de `ITEM_TYPES` al workspace `GFD26 - Prod`. La salida esperada es una lista de los ítems publicados; al final debería aparecer también el resultado de `unpublish_all_orphan_items`. Si algo falla, el error de la API suele indicar claramente qué ítem o qué permiso falta.

> **Aviso:** `--auth cli` usa tu sesión personal de Azure CLI, no el SP. Asegúrate de que tu usuario también tiene acceso al workspace Prod antes de hacer esta prueba, o añádete temporalmente con rol Admin.

## ✅ Checkpoint

- [ ] `parameter.yml` tiene los GUIDs reales de tu workspace y lakehouse Dev
- [ ] El despliegue local a Prod (`--auth cli`) termina sin errores y los ítems aparecen en GFD26 - Prod

## Errores típicos

| Síntoma | Causa | Solución |
| --- | --- | --- |
| `parameter.yml` no encontrado | La carpeta `workspace/` no es el `repository_directory` | Verificar que `--repository-directory` apunta a `src/workspace` o ajustar la ruta por defecto en `deploy.py` |
| `Item type not in scope` | El tipo de ítem no está en `ITEM_TYPES` | Añadir el tipo correspondiente a la lista `ITEM_TYPES` en `deploy.py` |
| Error de GUID incrustado tras desplegar | Los marcadores de `parameter.yml` no se sustituyeron | Reemplazar `00000000-...` y `11111111-...` por los GUIDs reales y volver a desplegar |

⬅️ [Módulo 05](05-service-principal.md) · ➡️ [Módulo 07 — Pipelines](07-pipelines-ado.md)
