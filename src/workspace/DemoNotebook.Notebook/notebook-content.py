# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "00000000-0000-0000-0000-000000000000",
# META       "default_lakehouse_name": "DemoLakehouse",
# META       "default_lakehouse_workspace_id": "11111111-1111-1111-1111-111111111111"
# META     }
# META   }
# META }

# CELL ********************

# Descarga el dataset público de clientes y lo carga como DataFrame de Spark
import pandas as pd

CSV_URL = (
    "https://raw.githubusercontent.com/microsoft/fabric-samples/main/"
    "docs-samples/data-engineering/dimension_customer.csv"
)

pdf = pd.read_csv(CSV_URL)
df = spark.createDataFrame(pdf)
print(f"Filas leídas: {df.count()}")

# CELL ********************

# Limpieza mínima: normaliza nombres de columna a snake_case
for col in df.columns:
    df = df.withColumnRenamed(col, col.strip().replace(" ", "_").lower())

# CELL ********************

# Escribe la tabla Delta en el lakehouse por defecto
df.write.mode("overwrite").format("delta").saveAsTable("dim_customer")
print("Tabla dim_customer escrita")
