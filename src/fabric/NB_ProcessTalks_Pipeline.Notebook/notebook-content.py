# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "1546a512-5301-4200-a7e8-774ac7cba230",
# META       "default_lakehouse_name": "LH_GlobalFabricDay",
# META       "default_lakehouse_workspace_id": "6b2d8c5d-8eb6-4b89-8f9e-5cfc82bdf2bb",
# META       "known_lakehouses": [
# META         {
# META           "id": "1546a512-5301-4200-a7e8-774ac7cba230"
# META         }
# META       ]
# META     }
# META   }
# META }

# CELL ********************

FABRIC_ENV:str      = "DEV"
WORKSPACE_ID:str    = "6b2d8c5d-8eb6-4b89-8f9e-5cfc82bdf2bb"
LAKEHOUSE_ID:str    = "1546a512-5301-4200-a7e8-774ac7cba230"
LAKEHOUSE_NAME:str  = "LH_GlobalFabricDay"

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from pyspark.sql.functions import col, upper, trim, lit, current_timestamp

RAW_TABLE_NAME    = "raw_talks"
SILVER_TABLE_NAME = "talks"

print(f"🌍 {FABRIC_ENV} | {RAW_TABLE_NAME} → silver.{SILVER_TABLE_NAME}")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

spark.sql("CREATE SCHEMA IF NOT EXISTS silver")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

abfss_path = f"abfss://{WORKSPACE_ID}@onelake.dfs.fabric.microsoft.com/{LAKEHOUSE_ID}/Tables/silver/{SILVER_TABLE_NAME}"
print(abfss_path)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

df_raw = spark.read.format("delta").table(RAW_TABLE_NAME)

df_silver = (
    df_raw
    .filter(col("is_talk") == True)
    .withColumn("room",    upper(trim(col("room"))))
    .withColumn("title",   trim(col("title")))
    .withColumn("speaker", trim(col("speaker")))
    .withColumn("processed_env", lit(FABRIC_ENV))
    .withColumn("processed_at",  current_timestamp())
    .drop("loaded_at")
)

df_silver.write.format("delta").mode("overwrite").option("overwriteSchema","true").save(abfss_path)
print(f"[{FABRIC_ENV}] ✅ Tabla Silver '{SILVER_TABLE_NAME}' — {df_silver.count()} charlas técnicas.")
df_silver.show(5, truncate=False)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
