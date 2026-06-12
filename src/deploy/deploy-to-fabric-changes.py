import os,argparse, requests, ast
from fabric_cicd import (
    FabricWorkspace, 
    publish_all_items, 
    change_log_level,
    append_feature_flag, 
    get_changed_items,
    append_feature_flag
)
from azure.identity import ClientSecretCredential

# funcion para devolver el ID del workspace
def get_workspace_id(p_ws_name, p_token):
    url = "https://api.fabric.microsoft.com/v1/workspaces"
    headers = {
        "Authorization": f"Bearer {p_token.token}",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)
    ws_id =''
    if response.status_code == 200:
        workspaces = response.json()["value"]
        for workspace in workspaces:
            if workspace["displayName"] == p_ws_name:
                ws_id = workspace["id"] 
                return workspace["id"]
        if ws_id == '':
            return f"Error: Workspace {p_ws_name} could not found."
    else:
        return f"Error: {response.status_code}, {response.text}"

# --- Feature Flags and Logging ---
append_feature_flag("enable_experimental_features")
append_feature_flag("enable_items_to_include")
# set log level
#change_log_level("DEBUG")

# parseo de argumentos para obtener los secretos necesarios para generar el token y el nombre del entorno objetivo. 
# El nombre del entorno es necesario para determinar el workspace a través de la variable de entorno que sigue la convención [entorno]WorkspaceName
parser = argparse.ArgumentParser(description='Process Azure Pipeline arguments.')
parser.add_argument('--aztenantid',type=str, help= 'tenant ID')
parser.add_argument('--azclientid',type=str, help= 'SP client ID')
parser.add_argument('--azspsecret',type=str, help= 'SP secret')
parser.add_argument('--target_env',type=str, help= 'target environment')
parser.add_argument('--items_in_scope',type=str, help= 'Defines the item types to be deployed')
parser.add_argument("--git_compare_ref", type=str, default="HEAD~1",
                    help="Rama o commit contra el que comparar. Ej: origin/dev, origin/pre")
parser.add_argument("--force_full_deploy", action="store_true", default=False,
                    help="Si se especifica, despliega todos los items ignorando git diff")
args = parser.parse_args()

# obtención del token de autenticación para llamar a la API de Fabric.
print('Obtaining token...')
token_credential = ClientSecretCredential(
    client_id=args.azclientid, 
    client_secret=args.azspsecret, 
    tenant_id=args.aztenantid
)

# obtención del nombre del entorno objetivo.
tgtenv = args.target_env
print(f'Target environment set to {tgtenv}')

# determina el workspace objetivo usando el variable group que almacena el nombre del workspace objetivo en una variable con la convención de nomenclatura "[tgtenv]WorkspaceName"
ws_name = f'{tgtenv}WorkspaceName'
print(f'Variable group to determine workspace is set to {ws_name}')

# define el nombre del workspace al que se va a desplegar basado en el valor en el variable group basado en el nombre del entorno objetivo. 
# Este variable group no está vinculado a un Key Vault por lo que los valores se pueden acceder a través de os.environ
workspace_name = os.environ[ws_name.upper()]
print(f'Obtaining GUID for {workspace_name}')

# generando el scope para obtener el token, basado en la documentación de Microsoft Graph, el scope para APIs de Microsoft es siempre [resource].default
resource = 'https://api.fabric.microsoft.com/'
scope = f'{resource}.default'
print(f'scope set to {scope}')
token = token_credential.get_token(scope)

# llamada a la función para obtener el ID del workspace.
lookup_response = get_workspace_id(workspace_name, token)
if lookup_response.startswith("Error"):
    errmsg=f"{lookup_response}. Perhaps workspace name is set incorrectly in the variable group of does not map to environment name + 'WorkspaceName'"
    raise ValueError(errmsg)
else:
    wks_id = lookup_response
    print(f"Workspace ID for {workspace_name} set to {wks_id}")

# establece la carpeta del repositorio basada en el valor del variable group de gitDirectory.
repository_directory = os.environ["GITDIRECTORY"]

# convierte el argumento de item types en una lista válida, eliminando los corchetes y dividiendo por comas. 
# También elimina espacios y comillas adicionales para asegurar que los nombres de los item types sean correctos.
item_types = [i.strip().strip('"').strip("'") for i in args.items_in_scope.strip("[]").split(",") if i.strip()]

# Inicializa el objeto FabricWorkspace con los parámetros requeridos
target_workspace = FabricWorkspace(
    workspace_id=wks_id,
    environment=tgtenv,
    repository_directory=repository_directory,
    item_type_in_scope=item_types,
    token_credential=token_credential,
)

# =============================================================================
# Despliegue SELECTIVO con get_changed_items() [EXPERIMENTAL]
#
# Usa "git diff" para detectar solo los items que cambiaron en este merge.
# Más rápido, pero requiere los feature flags experimentales y tiene riesgos
# si los items cambiados tienen dependencias con otros no desplegados.
# Recomendado para hotfixes o cuando el repo es muy grande.
#
# IMPORTANTE: si changed está vacío, NO llames a publish_all_items() sin
# items_to_include — equivaldría a un despliegue completo no intencionado.
# =============================================================================
if args.force_full_deploy:
    print("Despliegue completo forzado — ignorando git diff.")
    publish_all_items(target_workspace)
    print(f"Despliegue completo finalizado en {tgtenv.upper()}.")
else:
    print(f"\nDetectando cambios respecto a: {args.git_compare_ref}")
    changed = get_changed_items(
        repository_directory=target_workspace.repository_directory,
        git_compare_ref=args.git_compare_ref,
    )
    if changed:
        print(f"Items modificados: {changed}")
        publish_all_items(target_workspace, items_to_include=changed)
        print(f"Despliegue selectivo finalizado en {tgtenv.upper()}.")
    else:
        print("No se detectaron cambios en items de Fabric. Despliegue omitido.")