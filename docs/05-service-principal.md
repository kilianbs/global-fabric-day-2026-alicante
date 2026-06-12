# Módulo 05 — Service principal

El pipeline de Azure DevOps no puede autenticarse con tu usuario personal: no tiene sesión interactiva y, además, vincular un pipeline a una cuenta individual es una mala práctica. Lo que necesitas es una **identidad propia** — una *service principal* — que el pipeline pueda usar de forma segura y auditada. En este módulo la creas y la autorizas para publicar en el workspace de Prod.

## 1. Crear la app registration

Abre **Entra ID** (`portal.azure.com > Microsoft Entra ID > App registrations`) y haz clic en **New registration**. Dale un nombre descriptivo, por ejemplo `sp-fabric-cicd-demo`, deja el tipo de cuenta en *Accounts in this organizational directory only* y haz clic en **Register**.

No necesitas añadir permisos de API delegados en el panel *API permissions*. La librería `fabric-cicd` se autentica con las APIs de Fabric usando el **rol de workspace** que le asignarás en el paso 4, no permisos de Microsoft Graph.

Apunta ya el **Directory (tenant) ID** y el **Application (client) ID** que aparecen en la página de *Overview* de la app; los necesitarás en los módulos siguientes.

## 2. Autenticación con secreto de cliente

Si decides usar autenticación por secreto, ve a **Certificates & secrets > Client secrets > New client secret**. Pon una descripción y elige la caducidad que necesites.

> **Importante:** el valor del secreto solo se muestra una vez, justo después de crearlo. Cópialo ahora y guárdalo en un lugar seguro (por ejemplo, en una variable secreta del grupo de variables de ADO).

Con esta variante necesitas tres datos para el pipeline: **tenant ID**, **client ID** y el **secreto**. Es la opción más sencilla de entender, pero el secreto caduca y hay que rotarlo manualmente cada cierto tiempo.

## 3. Dar acceso al workspace Prod

Entra en el workspace **GFD_PRO** y abre **Manage access > Add people or groups**. Busca la app registration por su nombre (`sp-fabric-cicd-demo`) y asígnale el rol **Admin**.

El rol *Member* bastaría técnicamente para publicar ítems, pero en la demo el rol *Admin* evita fricciones si fabric-cicd necesita modificar configuraciones del workspace durante el despliegue. En un entorno de producción real, aplica el principio de mínimo privilegio y evalúa si *Member* o *Contributor* cubren tus necesidades.

## 4. Tenant setting

En el **Admin portal** de Fabric (`app.fabric.microsoft.com > Settings > Admin portal > Tenant settings`), localiza **Service principals can use Fabric APIs** y asegúrate de que está habilitado.

Para acotar el alcance del permiso, en lugar de habilitarlo para toda la organización, crea un grupo de seguridad en Entra ID, añade ahí el SP y activa el tenant setting solo para ese grupo. Así limitas qué service principals pueden llamar a las APIs de Fabric.

> **Nota:** los cambios en tenant settings pueden tardar hasta 15 minutos en propagarse. Si el SP devuelve 401 justo después de habilitarlo, espera un poco y vuelve a intentarlo.

## ✅ Checkpoint

- [ ] Tienes el tenant ID, el client ID y el secreto apuntados
- [ ] El SP aparece en Manage access del workspace GFD_PRO con rol Admin
- [ ] El tenant setting "Service principals can use Fabric APIs" está activo

## Errores típicos

| Síntoma | Causa | Solución |
| --- | --- | --- |
| 401 al desplegar | Tenant setting de SPs deshabilitado o propagación pendiente | Habilitarlo en el Admin portal; esperar ~15 min y reintentar |
| 403 / workspace not found | SP sin rol en el workspace | Añadirlo como Admin o Member en Manage access |

⬅️ [Módulo 04](04-git-integration.md) · ➡️ [Módulo 06 — fabric-cicd](06-fabric-cicd.md)
