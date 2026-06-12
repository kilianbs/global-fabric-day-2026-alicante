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

from pyspark.sql.functions import col, upper, trim, lit, current_timestamp

vl = notebookutils.variableLibrary.getLibrary("VL_GlobalFabricDay")

FABRIC_ENV        = vl.FABRIC_ENV
RAW_TABLE_NAME    = "raw_talks"
SILVER_TABLE_NAME = "silver.talks"

print(f"🌍 {FABRIC_ENV} | {RAW_TABLE_NAME} → {SILVER_TABLE_NAME}")

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

df_silver.write.format("delta").mode("overwrite").option("overwriteSchema","true").saveAsTable(SILVER_TABLE_NAME)
print(f"[{FABRIC_ENV}] ✅ Tabla Silver '{SILVER_TABLE_NAME}' — {df_silver.count()} charlas técnicas.")
df_silver.show(5, truncate=False)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
