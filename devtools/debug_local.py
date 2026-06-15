# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# The following is intended for developers of fabric-cicd to debug locally against the github repo

import sys
from pathlib import Path
from azure.identity import AzureCliCredential, AzurePowerShellCredential, ClientSecretCredential

from fabric_cicd import (
    FabricWorkspace,
    append_feature_flag,
    change_log_level,
    constants,
    publish_all_items,
    unpublish_all_orphan_items,
    get_changed_items,
)

# Uncomment to enable debug
# change_log_level()

# Uncomment to add feature flag
append_feature_flag("enable_shortcut_publish")
append_feature_flag("enable_experimental_features")
append_feature_flag("enable_items_to_include")

# The defined environment values should match the names found in the parameter.yml file
workspace_id = "fee199ea-d251-4f06-85a5-520f588f9c73"
environment = "pre"

# In this example, our workspace content sits within the root/sample/workspace directory
repository_directory = "fabric"

# Explicitly define which of the item types we want to deploy
item_type_in_scope = ["Notebook", "DataPipeline", "Lakehouse", "SemanticModel", "Report", "VariableLibrary"]

# Azure CLI auth - comment out to use a different auth method
token_credential = AzureCliCredential()

# Uncomment to use PowerShell auth
# token_credential = AzurePowerShellCredential()

# Uncomment to use SPN auth
client_id = ""
client_secret = ""
tenant_id = ""
token_credential = ClientSecretCredential(client_id=client_id, client_secret=client_secret, tenant_id=tenant_id)

constants.DEFAULT_API_ROOT_URL = "https://msitapi.fabric.microsoft.com"

# Initialize the FabricWorkspace object with the required parameters
target_workspace = FabricWorkspace(
    workspace_id=workspace_id,
    environment=environment,
    repository_directory=repository_directory,
    item_type_in_scope=item_type_in_scope,
    # Explicit token credential required for auth (choose one of the options above)
    token_credential=token_credential,
)

git_compare_ref = "origin/pre"

print(f"\nDetectando cambios respecto a: {git_compare_ref}")

changed = get_changed_items(
    repository_directory=target_workspace.repository_directory,
    git_compare_ref=git_compare_ref,
)

changed = get_changed_items(
    repository_directory=target_workspace.repository_directory,
    git_compare_ref=git_compare_ref,
)

if changed:
    print(f"Items modificados respecto a '{git_compare_ref}': {changed}")

# Uncomment to publish
# Publish all items defined in item_type_in_scope
# publish_all_items(target_workspace)

# Uncomment to unpublish
# Unpublish all items defined in scope not found in repository
# unpublish_all_orphan_items(target_workspace, item_name_exclude_regex=r"^DEBUG.*")
