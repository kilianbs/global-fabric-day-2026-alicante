# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from fabric_cicd import change_log_level
from fabric_cicd._parameter._utils import validate_parameter_file

# Descomenta para ver logs detallados
#change_log_level("DEBUG")

# Apunta a tu carpeta fabric/ donde está el parameter.yml
repository_directory = "fabric"

# Los mismos tipos que usas en tus pipelines
item_type_in_scope = ["Notebook", "DataPipeline", "Lakehouse", "SemanticModel", "Report", "VariableLibrary"]

# Set target environment
environment = "main"

validate_parameter_file(
    repository_directory=repository_directory,
    item_type_in_scope=item_type_in_scope,
    environment=environment,
)
