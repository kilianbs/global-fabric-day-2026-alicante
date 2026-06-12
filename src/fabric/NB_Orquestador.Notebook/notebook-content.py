# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {}
# META }

# CELL ********************

%run NB_SetDefaultLakehouse

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

DAG = {
    "activities": [
        {
            "name": "Load Talks",
            "path": "NB_LoadTalks",
            "timeoutPerCellInSeconds": 90,
            "args": {},
        },
        {
            "name": "Process Talks",
            "path": "NB_ProcessTalks",
            "timeoutPerCellInSeconds": 120,
            "args": {},
            "dependencies": ["Load Talks"]
        }
    ],
    "timeoutInSeconds": 43200, # max timeout for the entire DAG, default to 12 hours
    "concurrency": 12 # max number of notebooks to run concurrently, default to 3x CPU cores, 0 means unlimited
}
notebookutils.notebook.runMultiple(DAG, {"displayDAGViaGraphviz": True})

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
