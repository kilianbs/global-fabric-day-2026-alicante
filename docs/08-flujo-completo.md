# Módulo 08 — El flujo completo (guion de la demo)

Ya está todo montado: los workspaces, la integración con Git, el Service Principal, la librería fabric-cicd y los pipelines de ADO. Este módulo es el recorrido end-to-end que se muestra durante la charla. Cada paso corresponde a algo que el público ve en pantalla, en tiempo real.

## El recorrido

### 1. Branch out

Desde el workspace **GFD26 - Dev**, abre el panel de **Source control** y crea la rama `feature/demo-gfd` a partir de `dev`. Si tienes activada la opción de workspace aislado por rama, ADO creará automáticamente un workspace feature sincronizado con esa rama. Si no, puedes trabajar directamente en GFD26 - Dev apuntando a la nueva rama.

### 2. Cambio visible

Edita **DemoNotebook** para hacer un cambio que sea fácilmente comprobable en Prod. Por ejemplo:

- Añade una columna calculada al dataframe: `df["precio_con_iva"] = df["precio"] * 1.21`
- O modifica una medida DAX del modelo semántico DemoModel.

Lo importante es que el cambio sea visible en el informe o en la salida del notebook, para que el público pueda verificar con sus propios ojos que lo que aprobaron en el pipeline llegó a Prod sin intervención manual.

Una vez hecho el cambio, haz **commit** desde el workspace feature directamente (Source control > Commit). El commit queda en la rama `feature/demo-gfd` de Azure Repos.

### 3. PR feature → dev

En Azure Repos, abre un **Pull Request** de `feature/demo-gfd` hacia `dev` y completa el merge. En esta transición no se ejecuta el CI (la build validation solo cubre `main`), así que el merge es inmediato. El objetivo de este paso es integrar el cambio en la rama `dev` antes de promoverlo.

### 4. Update from Git en GFD26 - Dev

Vuelve al workspace **GFD26 - Dev** en Fabric y en el panel de Source control selecciona **Update from Git** (o *Sync*). El cambio del notebook aparece ahora en Dev. Este es el primer punto de verificación: el público puede abrir DemoNotebook en Dev y ver la columna nueva o la medida modificada.

### 5. PR dev → main

Abre un nuevo Pull Request de `dev` hacia `main` en Azure Repos. En cuanto se cree el PR, la **build validation** disparará el pipeline `CI - validacion` automáticamente. El CI instala `pyyaml` y ejecuta `deploy/validate.py` para comprobar que el `parameter.yml` y la estructura de ítems son correctos.

Cuando el CI termina en verde, el PR está listo para hacer merge. Complétalo.

### 6. El CD se dispara

El merge a `main` activa el trigger del pipeline `CD - deploy prod` porque los archivos modificados están bajo `workspace/**` o `deploy/**`. El stage `DeployProd` arranca y, al llegar al job `fabric_prod`, ADO detecta que el environment `fabric-prod` tiene una regla de aprobación: el stage queda en estado **Waiting for approval**.

**Este es el momento clave de la charla.** Muestra al público:

- El correo de notificación que ADO envía a los aprobadores.
- La pantalla del pipeline con el botón **Review > Approve**.

Aprueba el despliegue.

### 7. fabric-cicd publica en Prod

Tras la aprobación, el job continúa. El script `deploy/deploy.py` se ejecuta con `--workspace-id $(PROD_WORKSPACE_ID) --environment PROD`. Durante el despliegue puedes ver en el log del pipeline:

- Los ítems publicados uno a uno (Lakehouse, Notebook, DataPipeline, SemanticModel, Report, VariableLibrary).
- La sustitución del value set: fabric-cicd aplica `parameter.yml` y activa el value set `Prod` en DemoVariables.
- Los GUIDs reescritos: los marcadores `00000000-...` y `11111111-...` del `parameter.yml` se sustituyen por los GUIDs reales del workspace y el lakehouse Prod (referencias dinámicas `$items.Lakehouse.DemoLakehouse.$id` y `$workspace.$id`).

### 8. Verificar en Prod

Abre el workspace **GFD26 - Prod** en Fabric. Ejecuta **DemoPipeline** (o abre el informe directamente) y comprueba que el cambio que hiciste en el paso 2 está presente. La columna calculada existe, la medida DAX devuelve el valor actualizado.

Nadie ha tocado el workspace Prod a mano. Todo llegó a través del pipeline.

---

## Primera ejecución: cerrar el círculo de la Variable Library

En el primer despliegue a Prod, **DemoLakehouse aún no existe en Prod** antes de que fabric-cicd lo publique. Esto significa que el value set `Prod` de `DemoVariables` tiene todavía los GUIDs de marcador vacíos (los que configuraste en el módulo 03).

Después de ese primer despliegue exitoso:

1. Abre **GFD26 - Prod** y navega a DemoLakehouse. Copia su GUID de la URL (`app.fabric.microsoft.com/.../<guid>/...`).
2. Copia también el GUID del workspace `GFD26 - Prod` de la URL del workspace.
3. Vuelve a **GFD26 - Dev**, abre `DemoVariables` y edita el value set `Prod`: introduce los GUIDs reales del lakehouse y el workspace Prod.
4. Haz commit desde Source control, abre un PR de `dev` → `main` y completa el flujo completo (CI + aprobación CD).

A partir de ese segundo despliegue el value set `Prod` tiene valores reales y la Variable Library funciona correctamente en Prod.

> **Nota sobre `find_replace`:** los GUIDs incrustados en las definiciones de ítems (por ejemplo la conexión Direct Lake del modelo semántico) los resuelve automáticamente `parameter.yml` mediante las referencias dinámicas `$items.Lakehouse.DemoLakehouse.$id` y `$workspace.$id`. El value set cubre las variables que el pipeline resuelve en runtime, no los GUIDs incrustados en las definiciones.

## ✅ Checkpoint final

- [ ] Un cambio nacido en una rama feature es visible en el informe de Prod tras aprobar el pipeline
- [ ] Nadie ha tocado el workspace Prod a mano

## Si algo falla en directo (plan B)

| Síntoma | Causa probable | Qué hacer |
| --- | --- | --- |
| CI rojo en el PR | Error en `validate.py` (estructura de ítems o `parameter.yml` incorrecto) | Abrir el log del CI, leer el mensaje de error de `validate.py` y corregir el archivo señalado |
| El CD no se dispara tras el merge | El path filter no coincide (los archivos modificados no están en `workspace/**` ni `deploy/**`) | Hacer un cambio mínimo en `workspace/` o `deploy/` y abrir otro PR |
| Error 401 o 403 durante el despliegue | Credenciales del Service Principal incorrectas o permisos insuficientes en el workspace Prod | Revisar el módulo 05: client secret vigente, SP con rol Contributor en GFD26 - Prod |
| Un ítem no aparece en Prod tras el despliegue | El tipo de ítem no está en `ITEM_TYPES` o falta la carpeta en `workspace/` | Revisar `ITEM_TYPES` en `deploy.py` y verificar el log de `publish_all_items` |

⬅️ [Módulo 07](07-pipelines-ado.md) · 🏠 [Inicio](../README.md)
