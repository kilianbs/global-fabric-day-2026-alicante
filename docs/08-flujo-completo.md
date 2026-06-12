# Módulo 08 — El flujo completo (guion de la demo)

Ya está todo montado: los workspaces, la integración con Git, el Service Principal, la librería fabric-cicd y los pipelines de ADO. Este módulo es el recorrido end-to-end que se muestra durante la charla. Cada paso corresponde a algo que el público ve en pantalla, en tiempo real.

## El recorrido

### 1. Branch out

Desde el workspace **GFD_DEV**, abre el panel de **Source control** y crea la rama `feature/demo-gfd` a partir de `dev`. Si tienes activada la opción de workspace aislado por rama, ADO creará automáticamente un workspace feature sincronizado con esa rama. Si no, puedes trabajar directamente en GFD_DEV apuntando a la nueva rama.

### 2. Cambio visible

Edita **NB_LoadTalks** para hacer un cambio que sea fácilmente comprobable en GFD_PRO. Por ejemplo:

- Añade una columna calculada en la celda de limpieza del notebook, por ejemplo: `df = df.withColumn("ingestado_en", current_timestamp())` (importa `current_timestamp` de `pyspark.sql.functions`).
- O añade una celda de print con un mensaje identificable.

Lo importante es que el cambio sea visible en el informe o en la salida del notebook, para que el público pueda verificar con sus propios ojos que lo que aprobaron en el pipeline llegó a GFD_PRO sin intervención manual.

Una vez hecho el cambio, haz **commit** desde el workspace feature directamente (Source control > Commit) o desde VS Code. El commit queda en la rama `feature/demo-gfd` de Azure Repos.

### 3. PR feature → dev

En Azure Repos, abre un **Pull Request** de `feature/demo-gfd` hacia `dev` y completa el merge. El objetivo de este paso es integrar el cambio en la rama `dev` antes de promoverlo.

### 4. Update from Git en GFD_DEV

Vuelve al workspace **GFD_DEV** en Fabric y en el panel de Source control selecciona **Update from Git** (o *Sync*). El cambio del notebook aparece ahora en Dev. Este es el primer punto de verificación: el público puede abrir **NB_LoadTalks** en GFD_DEV y comprobar que el cambio está presente.

### 5. PR dev → pro

Abre un nuevo Pull Request de `dev` hacia `pro` en Azure Repos. Este es el **evento de promoción**: indica que lo que hay en `dev` está listo para producción.

Completa el merge.

### 6. El CD se dispara

El merge a `pro` activa el trigger del pipeline `deploy-to-fabric.yml` porque los archivos modificados están bajo `workspace/**` o `deploy/**`. El stage de despliegue arranca y, al llegar al job del environment `pro`, ADO detecta la regla de aprobación: el stage queda en estado **Waiting for approval**.

**Este es el momento clave de la charla.** Muestra al público:

- El correo de notificación que ADO envía a los aprobadores.
- La pantalla del pipeline con el botón **Review > Approve**.

Aprueba el despliegue.

### 7. fabric-cicd publica en GFD_PRO

Tras la aprobación, el job continúa. El script de despliegue se ejecuta apuntando al workspace GFD_PRO. Durante el despliegue puedes ver en el log del pipeline los ítems publicados uno a uno (Lakehouse, Notebook, DataPipeline, SemanticModel, Report, VariableLibrary).

Los GUIDs del value set `pro` (`WORKSPACE_ID` y `LAKEHOUSE_ID`) los sustituye `parameter.yml` automáticamente en cada despliegue: toma los GUIDs del workspace y el lakehouse destino usando los tokens `$workspace.$id` e `$items.Lakehouse.LH_GlobalFabricDay.$id`. No hay que editarlos a mano. Ver módulo 06 para el detalle de cómo funciona este mecanismo.

### 8. Verificar en GFD_PRO

Abre el workspace **GFD_PRO** en Fabric. Ejecuta **PL_Orquestador** (o abre el informe **RPT_GlobalFabricDay** directamente) y comprueba que el cambio que hiciste en el paso 2 está presente.

Nadie ha tocado el workspace GFD_PRO a mano. Todo llegó a través del pipeline.

---

## Otros caminos de la demo

Para demostrar los otros caminos del módulo 07, puedes: (a) modificar un solo ítem y ejecutar el pipeline de cambios para ver cómo detecta solo ese ítem; (b) lanzar manualmente el pipeline selectivo con `NB_SetDefaultLakehouse.Notebook` para redesplegar un único notebook sin tocar el resto.

---

## ✅ Checkpoint final

- [ ] Un cambio nacido en una rama feature es visible en GFD_PRO tras aprobar el pipeline
- [ ] Nadie ha tocado el workspace GFD_PRO a mano

## Si algo falla en directo (plan B)

| Síntoma | Causa probable | Qué hacer |
| --- | --- | --- |
| El CD no se dispara tras el merge | El path filter no coincide (los archivos modificados no están en `workspace/**` ni `deploy/**`) | Hacer un cambio mínimo en `workspace/` o `deploy/` y abrir otro PR |
| Error 401 o 403 durante el despliegue | Credenciales del Service Principal incorrectas o permisos insuficientes en el workspace GFD_PRO | Revisar el módulo 05: client secret vigente, SP con rol Contributor en GFD_PRO |
| Un ítem no aparece en GFD_PRO tras el despliegue | El tipo de ítem no está en `ITEM_TYPES` o falta la carpeta en `workspace/` | Revisar `ITEM_TYPES` en `deploy.py` y verificar el log de `publish_all_items` |
| El pipeline queda bloqueado en aprobación | El aprobador no recibió el correo | Buscar el pipeline en ADO y aprobar manualmente desde la pestaña Pipelines |

⬅️ [Módulo 07](07-pipelines-ado.md) · 🏠 [Inicio](../README.md)
