# Módulo 07 — Pipelines de Azure DevOps

En este módulo configuras los pipelines de Azure DevOps que automatizan el despliegue de los ítems de Fabric al workspace `GFD_PRO`. Hay tres caminos según el escenario: desplegar todo, desplegar solo lo que cambió, o desplegar ítems concretos. Todos comparten la misma preparación previa.

## 1. Preparación común

Antes de registrar cualquier pipeline hay que crear los variable groups y el environment en ADO.

### 1a. Variable groups (Library > + Variable group)

Los pipelines leen la configuración a través de dos variable groups. Los nombres son exactos; el script Python los busca por ese nombre.

**Variable group `fabric_cicd_group_sensitive`**

Ve a **Pipelines > Library > Variable groups** y crea un nuevo group con ese nombre exacto. Añade estas tres variables:

| Variable | Descripción | ¿Secreta? |
| --- | --- | --- |
| `pro-aztenantid` | GUID del tenant de Azure | No |
| `pro-azclientid` | Application (client) ID del Service Principal | No |
| `pro-azspsecret` | Valor del secreto del Service Principal | **Sí 🔒** |

Para marcar `pro-azspsecret` como secreta, haz clic en el icono del candado a la derecha del campo de valor. ADO la enmascarará en los logs y la tratará como dato sensible.

**Variable group `fabric_cicd_group_non_sensitive`**

Crea un segundo group con ese nombre exacto. Añade estas dos variables:

| Variable | Valor | ¿Secreta? |
| --- | --- | --- |
| `proWorkspaceName` | `GFD_PRO` | No |
| `gitDirectory` | `fabric` | No |

> **¿Por qué estos nombres?** El script Python lee `os.environ["PROWORKSPACENAME"]` (ADO expone las variables en mayúsculas) para determinar el workspace destino. La variable `gitDirectory` le dice en qué carpeta del repo buscar los ítems de Fabric.

### 1b. Environment `pro` con aprobación manual

Ve a **Pipelines > Environments > New environment**, nómbralo `pro` y selecciona el tipo *None*. Una vez creado:

1. Entra en el environment recién creado y abre **Approvals and checks**.
2. Haz clic en el `+` y selecciona **Approvals**.
3. Añádete como aprobador (puedes añadir más personas si lo necesitas).
4. Guarda.

A partir de ahora el stage de despliegue quedará pausado en el estado *Waiting for approval* hasta que alguien del grupo aprobador lo confirme. Este es el momento de la demo donde el público verá el botón **Approve** en pantalla.

## 2. Los tres caminos de despliegue

Los tres pipelines despliegan al mismo workspace (`GFD_PRO`) y comparten los variable groups anteriores. La diferencia está en cuándo se ejecutan y qué ítems despliegan.

### Camino 1 — Deploy de todo (pipeline por defecto)

| | |
| --- | --- |
| **YAML** | `pipelines/deploy-to-fabric.yml` |
| **Script** | `deploy/deploy-to-fabric.py` |
| **Trigger** | Automático: push o merge a la rama `pro` con cambios en `fabric/**` |
| **Qué despliega** | Todos los ítems del directorio `fabric/` |

**Cuándo usarlo:** primera puesta en marcha, cuando hay muchos cambios acumulados, o cuando se quiere la seguridad de que el workspace queda exactamente igual que el repo. Es el enfoque más simple y predecible.

**Cómo registrarlo en ADO:**

Ve a **Pipelines > New pipeline > Azure Repos Git**, elige el repositorio `Global Fabric Day` y selecciona **Existing Azure Pipelines YAML file**. En la rama `dev`, introduce la ruta `pipelines/deploy-to-fabric.yml` y finaliza la creación.

> Este es el pipeline que se deja habilitado para la demo.

---

### Camino 2 — Deploy de cambios

| | |
| --- | --- |
| **YAML** | `pipelines/deploy-to-fabric-changes.yml` |
| **Script** | `deploy/deploy-to-fabric-changes.py` |
| **Trigger** | Automático: push o merge a la rama `pro` con cambios en `fabric/**` |
| **Qué despliega** | Solo los ítems con diferencias respecto al commit anterior (`HEAD~1`) |

**Cuándo usarlo:** repos grandes o equipos con despliegues frecuentes donde redesplegar todo en cada push no es práctico. El script compara el estado actual con `HEAD~1` y solo envía a Fabric los ítems que cambiaron.

**Advertencia:** este pipeline requiere activar feature flags experimentales de `fabric-cicd` (`enable_experimental_features` y `enable_items_to_include`). Si un ítem modificado tiene dependencias con otros ítems que no se están desplegando en esa ejecución, pueden aparecer errores de referencia.

El parámetro `force_full_deploy` permite forzar un despliegue completo cuando sea necesario, sin cambiar el YAML.

**Nota para la demo:** el Camino 1 y el Camino 2 tienen el mismo trigger automático. Si registras ambos pipelines y los dejas habilitados, los dos dispararán en paralelo al mismo push. Recomendación: mantener solo uno habilitado en cada momento (**Pipeline > ... > Settings > Trigger disabled** para el que no se use).

**Cómo registrarlo en ADO:**

Mismo proceso que el Camino 1 pero con la ruta `pipelines/deploy-to-fabric-changes.yml`.

---

### Camino 3 — Deploy selectivo

| | |
| --- | --- |
| **YAML** | `pipelines/deploy-to-fabric-selected-items.yml` |
| **Script** | `deploy/deploy-to-fabric-selective.py` |
| **Trigger** | `trigger: none` — solo manual desde la interfaz de ADO |
| **Qué despliega** | Los ítems especificados por nombre en el parámetro `items_to_deploy` |

**Cuándo usarlo:** hotfixes urgentes o cuando se sabe exactamente qué ítem hay que redesplegar sin tocar el resto del workspace.

**Cómo ejecutarlo:** ve al pipeline en ADO y haz clic en **Run pipeline**. En el panel lateral aparece el parámetro `items_to_deploy`: introduce los nombres de los ítems separados por comas en formato `Nombre.Tipo`. Por ejemplo:

```
NB_SetDefaultLakehouse.Notebook, RPT_GlobalFabricDay.Report
```

**Cómo registrarlo en ADO:**

Mismo proceso que los anteriores pero con la ruta `pipelines/deploy-to-fabric-selected-items.yml`.

---

### Tabla resumen

| Camino | Fichero | Trigger | Qué despliega |
| --- | --- | --- | --- |
| Deploy de todo | `pipelines/deploy-to-fabric.yml` | Automático (push a `pro` con cambios en `fabric/**`) | Todos los ítems |
| Deploy de cambios | `pipelines/deploy-to-fabric-changes.yml` | Automático (mismo) | Solo ítems con diff vs último commit |
| Deploy selectivo | `pipelines/deploy-to-fabric-selected-items.yml` | Manual | Ítems especificados por nombre |

## ✅ Checkpoint

- [ ] Variable group `fabric_cicd_group_sensitive` creado con `pro-aztenantid`, `pro-azclientid` y `pro-azspsecret` (esta última marcada como secreta)
- [ ] Variable group `fabric_cicd_group_non_sensitive` creado con `proWorkspaceName = GFD_PRO` y `gitDirectory = fabric`
- [ ] Environment `pro` creado con al menos un aprobador configurado
- [ ] Los tres pipelines registrados en ADO
- [ ] Pipeline por defecto (`deploy-to-fabric.yml`) verificado: al hacer un push de prueba a `pro` con un cambio en `fabric/`, el pipeline dispara y se detiene pidiendo aprobación en el environment `pro`

## Errores típicos

| Síntoma | Causa | Solución |
| --- | --- | --- |
| "This pipeline needs permission to access a resource" o "could not access variable group" | Los variable groups o el environment `pro` no han sido autorizados en el primer run | Abrir el pipeline pausado y hacer clic en **Permit** para cada recurso |
| El pipeline no se dispara al mergear a `pro` | El path filter del trigger no coincide con los archivos cambiados | Verificar que los cambios están en `fabric/**`; cambios en otras rutas (p. ej. `docs/`) no disparan el pipeline |
| El Camino 2 falla con un error de referencia a un ítem | Un ítem modificado depende de otro no incluido en el despliegue diferencial | Usar el parámetro `force_full_deploy` o cambiar al Camino 1 para esa ejecución |
| Los dos pipelines automáticos disparan a la vez | Camino 1 y Camino 2 tienen el mismo trigger y están ambos habilitados | Deshabilitar el trigger del pipeline que no se usa en ese momento (Pipeline > Settings > Trigger disabled) |
| El Camino 3 no aparece en la lista de runs automáticos | Es correcto: `trigger: none` significa que solo se ejecuta manualmente | Ejecutarlo desde **Run pipeline** en la interfaz de ADO |

⬅️ [Módulo 06](06-fabric-cicd.md) · ➡️ [Módulo 08 — Flujo completo](08-flujo-completo.md)
