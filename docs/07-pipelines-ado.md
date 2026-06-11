# Módulo 07 — Pipelines de Azure DevOps

En este módulo configuras los dos pipelines de Azure DevOps que automatizan la validación y el despliegue de la demo. Al terminar, cada PR hacia `main` ejecutará el CI automáticamente, y cada merge a `main` lanzará el CD que espera tu aprobación antes de publicar en Prod.

## 1. Variable group

El pipeline CD necesita acceder a varios secretos y configuraciones que no deben estar en el código. Para ello usarás un **Variable group** en ADO.

Ve a **Pipelines > Library > Variable groups** y crea uno nuevo con el nombre exacto `fabric-cicd-demo`. Añade las siguientes variables:

| Variable | Descripción | ¿Secreta? |
| --- | --- | --- |
| `PROD_WORKSPACE_ID` | GUID del workspace `GFD26 - Prod` | No |
| `AZURE_TENANT_ID` | ID del tenant de Entra ID (solo variante `secret`) | No |
| `AZURE_CLIENT_ID` | Client ID de la app registration (solo variante `secret`) | No |
| `AZURE_CLIENT_SECRET` | Client secret de la app registration (solo variante `secret`) | **Sí — marcarla con el candado** |

Para marcar `AZURE_CLIENT_SECRET` como secreta, haz clic en el icono del candado que aparece a la derecha del campo de valor. ADO la enmascarará en los logs y la tratará como dato sensible.

> Los valores de `AZURE_TENANT_ID`, `AZURE_CLIENT_ID` y `AZURE_CLIENT_SECRET` son los mismos que configuraste en el módulo 05 al crear la app registration. Si usas la variante federada (ver §5), solo necesitas `PROD_WORKSPACE_ID`.

## 2. Environment con aprobación

El CD despliega a través de un **Environment** de ADO, que permite bloquear la ejecución hasta que una persona apruebe manualmente. Así nadie puede publicar en Prod por accidente.

Ve a **Pipelines > Environments > New environment**, nómbralo `fabric-prod` y selecciona el tipo *None* (no necesita recursos de Kubernetes ni VMs). Una vez creado:

1. Entra en el environment recién creado y abre **Approvals and checks**.
2. Haz clic en el `+` para añadir un check y selecciona **Approvals**.
3. Añádete a ti mismo como aprobador (puedes añadir otras personas del equipo si lo necesitas).
4. Guarda. A partir de ahora el stage `DeployProd` del CD quedará pausado en el estado *Waiting for approval* hasta que alguien del grupo aprobador confirme.

Este es el momento de la charla donde el público verá el correo y la pantalla de aprobación.

## 3. Crear los dos pipelines

Los archivos YAML ya están en el repositorio bajo `pipelines/`. Solo necesitas registrarlos en ADO.

**Pipeline CI — "CI - validacion"**

Ve a **Pipelines > New pipeline**, selecciona **Azure Repos Git**, elige tu repositorio y luego **Existing Azure Pipelines YAML file**. Selecciona la ruta `pipelines/azure-pipelines-ci.yml` y finaliza la creación. Renombra el pipeline a `CI - validacion` desde el menú de opciones del pipeline (los tres puntos en la lista de pipelines).

**Pipeline CD — "CD - deploy prod"**

Repite el proceso pero seleccionando `pipelines/azure-pipelines-cd.yml`. Renómbralo a `CD - deploy prod`.

**Primer run del CD y autorizaciones**

La primera vez que el CD intente ejecutarse, ADO te pedirá que autorices el acceso al variable group `fabric-cicd-demo` y al environment `fabric-prod`. Haz clic en **Permit** para cada uno cuando aparezca la pantalla de autorización. Este paso solo ocurre una vez: a partir de ahí el pipeline tiene acceso permanente a esos recursos.

> Si el pipeline falla antes de llegar al stage de despliegue con el mensaje "This pipeline needs permission to access a resource", es precisamente esta autorización la que falta (ver la sección **Errores típicos** de este módulo).

## 4. Activar la build validation en main

Con el CI creado, vuelve a lo que viste en el módulo 04 §5 para terminar de conectar las piezas.

Ve a **Repos > Branches**, busca la rama `main` y abre sus **Branch policies**. En la sección **Build validation** añade una nueva regla:

- **Build pipeline**: selecciona `CI - validacion`
- **Trigger**: Automatic
- **Policy requirement**: Required

A partir de este momento, cualquier PR cuya rama base sea `main` disparará automáticamente el CI. El PR no podrá completarse hasta que el pipeline termine en verde.

> Recuerda que `azure-pipelines-ci.yml` tiene `trigger: none`, lo que significa que **solo** se ejecuta como build validation, nunca por push directo. Es el comportamiento correcto: el CI es exclusivo de los PRs.

## 5. Las dos variantes de auth en el YAML

El CD tiene un parámetro `authMode` que acepta dos valores: `secret` y `federated`. El valor por defecto es `secret`.

**Variante A — `secret` (Service Principal con client secret)**

Usa las variables `AZURE_TENANT_ID`, `AZURE_CLIENT_ID` y `AZURE_CLIENT_SECRET` del variable group para autenticarse directamente contra la API de Fabric. Es la opción más sencilla de configurar y funciona en cualquier tenant sin configuración adicional en ADO. El script `deploy.py` se invoca con `--auth secret`.

**Variante B — `federated` (Workload Identity Federation)**

Usa la service connection `sc-fabric-cicd-demo` que configuraste en el módulo 05 §3 con Workload Identity Federation. En este caso no hay secreto que rotar: ADO genera un token de corta duración en cada ejecución. El step usa la tarea `AzureCLI@2` con `azureSubscription: sc-fabric-cicd-demo`, que inyecta las credenciales en la sesión de Azure CLI; el script `deploy.py` recibe `--auth cli` y las consume de ahí.

Para cambiar la variante en una ejecución manual ve al botón **Run pipeline** del CD y modifica el parámetro `authMode` en el panel lateral. Si quieres cambiar el valor por defecto de forma permanente, edita el campo `default` en el YAML.

| Variante | Cuándo usarla |
| --- | --- |
| `secret` | Configuración rápida, tenant sin Workload Identity Federation configurado |
| `federated` | Entornos de producción donde no quieres gestionar la rotación de secretos |

## ✅ Checkpoint

- [ ] Un PR de prueba hacia `main` ejecuta el CI automáticamente
- [ ] El CD aparece en Pipelines y tiene acceso al variable group y al environment

## Errores típicos

| Síntoma | Causa | Solución |
| --- | --- | --- |
| "This pipeline needs permission to access a resource" o "could not access variable group" | El variable group `fabric-cicd-demo` o el environment `fabric-prod` no han sido autorizados | Abrir el pipeline pausado y hacer clic en **Permit** para cada recurso |
| El CD no se dispara al mergear a `main` | El path filter del trigger no coincide con los archivos cambiados | Verificar que los cambios están en `workspace/**` o `deploy/**`; los cambios en otras rutas (p. ej. `docs/`) no disparan el CD |
| El CI no se ejecuta en el PR | La build validation no está configurada en las branch policies de `main` | Seguir el paso §4 de este módulo |
| El CI falla con `ModuleNotFoundError: No module named 'yaml'` | `pyyaml` no se instaló antes de ejecutar `validate.py` | El YAML del CI instala `pyyaml` explícitamente; verificar que el step de instalación no se saltó |

⬅️ [Módulo 06](06-fabric-cicd.md) · ➡️ [Módulo 08 — Flujo completo](08-flujo-completo.md)
