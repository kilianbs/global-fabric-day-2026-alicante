# Módulo 04 — Conectar el workspace a Git

En este módulo conectas **GFD26 - Dev** a una rama del repositorio de Azure Repos, exploras la estructura de carpetas que Fabric genera al exportar los ítems y practicas el flujo completo de trabajo en ramas: branch-out, commit, pull request y actualización del workspace. Al terminar tendrás la base para que el pipeline de CI/CD del módulo 07 pueda actuar sobre el repositorio.

---

## 1. Crear el repositorio en Azure DevOps

Abre tu organización de Azure DevOps (`dev.azure.com/<tu-organización>`), navega hasta el proyecto que usarás para la demo y ve a **Repos**. Si el proyecto no tiene ningún repositorio todavía, ADO habrá creado uno con el nombre del proyecto; puedes usarlo o crear uno nuevo desde **Repos > + New repository**.

Nombra el repositorio exactamente `fabric-cicd-demo` e inicialízalo con un **README** (esto crea la rama `main` automáticamente). Una vez creado el repo, añade la rama `dev` desde la interfaz de ramas: ve a **Repos > Branches**, haz clic en **+ New branch**, escribe `dev` y elige `main` como origen.

El repositorio de GitHub que estás leyendo contiene los archivos de despliegue y los pipelines de CI/CD. Copia el contenido de las carpetas `src/deploy` y `src/pipelines` a la **raíz** del repo de ADO bajo los nombres `deploy/` y `pipelines/` respectivamente. El pipeline de CI espera encontrar `deploy/validate.py` y `pipelines/azure-pipelines-ci.yml` en esas rutas. Puedes hacer esta copia con una clonada local y un push, o directamente desde la interfaz web de ADO subiendo los archivos uno a uno.

*(captura pendiente: assets/04-ado-repo-branches.png)*

---

## 2. Conectar "GFD26 - Dev" a la rama dev

Con el repositorio listo, ve al workspace **GFD26 - Dev** en Fabric. Haz clic en el nombre del workspace en la barra lateral, luego en **Workspace settings** (el icono de engranaje) y abre la pestaña **Git integration**.

Rellena los campos del formulario de conexión:

- **Organization** — tu organización de ADO.
- **Project** — el proyecto donde creaste `fabric-cicd-demo`.
- **Repository** — `fabric-cicd-demo`.
- **Branch** — `dev`.
- **Git folder** — `/workspace` (esta subcarpeta es la que Fabric usará para leer y escribir los ítems; si la dejas en raíz, los archivos de `deploy/` y `pipelines/` quedarán mezclados con los ítems de Fabric).

Haz clic en **Connect and sync**. Fabric detectará que la carpeta `/workspace` está vacía y te pedirá que elijas entre exportar los ítems del workspace al repo o importar lo que hay en el repo al workspace. Selecciona **Export workspace items to Git**: los seis ítems que creaste en el módulo 03 se exportarán como commit inicial a la rama `dev`.

*(captura pendiente: assets/04-git-connect.png)*

---

## 3. Explora lo que Fabric ha escrito

Abre el repositorio en ADO y navega a la rama `dev`. Dentro de la carpeta `workspace/` verás una subcarpeta por cada ítem con el formato `<Nombre>.<Tipo>`. Examina algunas de ellas:

- **DemoLakehouse.Lakehouse/** — contiene solo el archivo `.platform` con los metadatos del ítem (`type`, `displayName`) y su `logicalId`. Los lakehouses no tienen definición de contenido exportable: las tablas viven en OneLake, no en Git.
- **DemoNotebook.Notebook/** — incluye `.platform` y `notebook-content.py`. Este último contiene las celdas que pegaste en el módulo 03, precedidas del bloque `# META` con la configuración del kernel y el lakehouse por defecto.
- **DemoVariables.VariableLibrary/** — exporta cuatro archivos: `.platform`, `variables.json` (las variables y sus valores de Dev), `settings.json` (el value set activo y el orden de los value sets) y la subcarpeta `valueSets/Prod.json` con los overrides para producción.
- **DemoPipeline.DataPipeline/** — contiene `.platform` y `pipeline-content.json` con la definición de las actividades, incluyendo la expresión `@pipeline().libraryVariables.DemoVariables.workspace_id`.

Compara estas carpetas con `../src/workspace/` del repositorio de GitHub: son equivalentes. La diferencia es que los GUIDs de tu entorno serán distintos; los marcadores de posición del repo de referencia (`00000000-...`) se usan en el módulo 05 para explicar cómo fabric-cicd los sustituye.

*(captura pendiente: assets/04-repo-structure.png)*

---

## 4. Flujo branch-out (feature workspaces)

Fabric permite crear un workspace temporal vinculado a una rama de feature en un solo gesto. Desde el workspace **GFD26 - Dev**, fíjate en la esquina inferior izquierda: aparece el nombre de la rama (`dev`) con un icono de ramificación. Haz clic en él y selecciona **Branch out to new workspace**.

Fabric te pedirá el nombre de la rama; escribe algo como `feature/prueba-notebook`. Automáticamente creará la rama en ADO a partir de `dev` y un workspace nuevo sincronizado con esa rama. Trabaja en ese workspace como si fuera tu entorno personal de desarrollo.

Haz un cambio pequeño para practicar el flujo: por ejemplo, abre DemoNotebook en el workspace feature, añade una celda con un `print("hola")` y guárdala. Luego abre el panel **Source control** (icono de Git en la barra izquierda), escribe un mensaje de commit como `chore: celda de prueba` y haz clic en **Commit**. El cambio queda registrado en la rama `feature/prueba-notebook` del repo de ADO.

Abre ADO, crea un **Pull Request** desde `feature/prueba-notebook` hacia `dev` y complétalo (puedes aprobarlo tú mismo si eres el único revisor). Una vez que el PR hace merge, vuelve al workspace **GFD26 - Dev**, abre **Source control** y haz clic en **Update from Git**: Fabric descarga los cambios de la rama `dev` y actualiza los ítems del workspace. La actualización es manual en esta demo a propósito, para que quede claro el modelo mental; si quisieras automatizarla, la API de Fabric expone un endpoint para ello, aunque eso está fuera del alcance de este módulo.

*(captura pendiente: assets/04-branch-out.png)*

---

## 5. Políticas de rama en main

Las políticas de rama de ADO evitan que alguien publique directamente en `main` sin pasar por un pull request revisado. Ve a **Repos > Branches**, localiza la rama `main` y haz clic en los tres puntos a su derecha > **Branch policies**.

Activa al menos estas dos políticas:

- **Require a minimum number of reviewers** — pon el mínimo en **1**. En un equipo real usa al menos 2; para la demo con un único contribuidor puedes marcar "Allow requestors to approve their own changes" como excepción.
- **Build validation** — haz clic en **+ Add build policy**, selecciona el pipeline `azure-pipelines-ci.yml` (que importarás desde `pipelines/azure-pipelines-ci.yml` en el módulo 07) y déjalo en modo **Required**. El pipeline ejecuta `deploy/validate.py`, que comprueba la coherencia del `parameter.yml` y la estructura de los ítems antes de permitir el merge.

> **Nota:** el pipeline de CI aún no existe en ADO en este momento; vuelve a esta sección tras el módulo 07 para activar la build validation.

*(captura pendiente: assets/04-branch-policies.png)*

---

## ✅ Checkpoint

- [ ] El repo ADO tiene la carpeta `/workspace` con todos los ítems del módulo 03 tras el commit inicial
- [ ] Un cambio hecho vía branch-out ha llegado a `dev` por PR y el workspace GFD26 - Dev lo muestra tras "Update from Git"

---

## Errores típicos

| Síntoma | Causa | Solución |
| --- | --- | --- |
| Los ítems de Fabric aparecen mezclados con `deploy/` y `pipelines/` en el repo | Se dejó la carpeta Git en `/` en lugar de `/workspace` al conectar | Desconecta el workspace (Git integration > Disconnect), borra los archivos exportados a la raíz del repo y vuelve a conectar especificando `/workspace` como carpeta Git |
| "Update from Git" no aparece o no tiene efecto | No hay cambios nuevos en la rama `dev` respecto al estado actual del workspace | Asegúrate de que el PR hacia `dev` se ha completado y de que hay al menos un commit nuevo; el botón solo aparece cuando existe divergencia entre el repo y el workspace |
| El workspace feature no se crea | La rama ya existe en ADO con ese nombre | Elige un nombre de rama distinto o borra la rama existente antes de hacer branch-out |
| El commit inicial falla con error de permisos | La service principal o el usuario de Fabric no tiene permisos de escritura en el repo de ADO | En ADO, ve a Project settings > Repos > Permissions y concede al usuario el rol Contributor sobre el repo `fabric-cicd-demo` |

---

⬅️ [Módulo 03](03-contenido-demo.md) · ➡️ [Módulo 05 — Service principal](05-service-principal.md)
