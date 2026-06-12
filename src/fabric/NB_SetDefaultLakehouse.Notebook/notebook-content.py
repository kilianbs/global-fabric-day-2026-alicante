# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse_name": "",
# META       "default_lakehouse_workspace_id": "",
# META       "known_lakehouses": []
# META     }
# META   }
# META }

# MARKDOWN ********************

# # ⚙️ SetDefaultLakehouse
# # Vincula el Lakehouse por defecto en tiempo de ejecución
# # usando los valores del value set activo en VL_GlobalFabricDay.
# # No hay ningún ID hardcodeado en este notebook.

# CELL ********************

# MAGIC %%configure
# MAGIC {
# MAGIC   "defaultLakehouse": {
# MAGIC     "name": {
# MAGIC       "variableName": "$(/**/VL_GlobalFabricDay/LAKEHOUSE_NAME)" 
# MAGIC     },
# MAGIC     "id": {
# MAGIC       "variableName": "$(/**/VL_GlobalFabricDay/LAKEHOUSE_ID)"
# MAGIC     },
# MAGIC     "workspaceId": {
# MAGIC       "variableName": "$(/**/VL_GlobalFabricDay/WORKSPACE_ID)"
# MAGIC     }
# MAGIC   }
# MAGIC }

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

vl = notebookutils.variableLibrary.getLibrary("VL_GlobalFabricDay")

FABRIC_ENV    = vl.FABRIC_ENV
LAKEHOUSE_ID  = vl.LAKEHOUSE_ID
WORKSPACE_ID  = vl.WORKSPACE_ID

print(f"🌍 Entorno activo  : {FABRIC_ENV}")
print(f"🏠 Workspace ID    : {WORKSPACE_ID}")
print(f"🔑 Lakehouse ID    : {LAKEHOUSE_ID}")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
