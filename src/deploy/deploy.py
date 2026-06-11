"""Despliegue de ítems de Fabric con fabric-cicd.

Uso:
  python deploy.py --workspace-id <GUID> --environment PROD --auth secret
  python deploy.py --workspace-id <GUID> --environment PROD --auth cli

Auth "secret": requiere AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET.
Auth "cli": usa la sesión activa de Azure CLI (variante federada vía AzureCLI@2).
"""

import argparse
import os
import sys

from azure.identity import AzureCliCredential, ClientSecretCredential
from fabric_cicd import FabricWorkspace, publish_all_items, unpublish_all_orphan_items

ITEM_TYPES = [
    "VariableLibrary",
    "Lakehouse",
    "Notebook",
    "DataPipeline",
    "SemanticModel",
    "Report",
]


def build_credential(auth_mode: str):
    if auth_mode == "secret":
        for var in ("AZURE_TENANT_ID", "AZURE_CLIENT_ID", "AZURE_CLIENT_SECRET"):
            if not os.environ.get(var):
                sys.exit(f"Falta la variable de entorno {var}")
        return ClientSecretCredential(
            tenant_id=os.environ["AZURE_TENANT_ID"],
            client_id=os.environ["AZURE_CLIENT_ID"],
            client_secret=os.environ["AZURE_CLIENT_SECRET"],
        )
    return AzureCliCredential()


def main() -> None:
    parser = argparse.ArgumentParser(description="Despliega ítems de Fabric con fabric-cicd")
    parser.add_argument("--workspace-id", required=True, help="GUID del workspace destino")
    parser.add_argument("--environment", required=True, help="Entorno destino, p. ej. PROD")
    parser.add_argument("--auth", choices=["secret", "cli"], default="secret")
    parser.add_argument(
        "--repository-directory",
        default=os.path.join(os.path.dirname(__file__), "..", "workspace"),
        help="Carpeta con las definiciones de ítems",
    )
    args = parser.parse_args()

    workspace = FabricWorkspace(
        workspace_id=args.workspace_id,
        environment=args.environment,
        repository_directory=os.path.abspath(args.repository_directory),
        item_type_in_scope=ITEM_TYPES,
        token_credential=build_credential(args.auth),
    )

    publish_all_items(workspace)
    unpublish_all_orphan_items(workspace)


if __name__ == "__main__":
    main()
