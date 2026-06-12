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

from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.sql.functions import col, when, lit, current_timestamp
from datetime import date

spark = SparkSession.builder.getOrCreate()

vl = notebookutils.variableLibrary.getLibrary("VL_GlobalFabricDay")

FABRIC_ENV     = vl.FABRIC_ENV
RAW_TABLE_NAME = "raw_talks"

print(f"🌍 Entorno: {FABRIC_ENV} | Tabla destino: {RAW_TABLE_NAME}")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

talks_data = [
    ("AUD-01","09:00","09:15","Auditorio","Bienvenida y presentación",None,False,False,None),
    ("AUD-02","09:15","10:00","Auditorio","Agentes en acción: Databricks vs Microsoft Fabric","Alberto Díaz",True,False,"IA & Agentes"),
    ("AUD-03","10:00","10:45","Auditorio","Databricks vs Fabric. OneLake to rule them all","Miguel Teruel & David Noguera",True,False,"Arquitectura"),
    ("AUD-04","10:45","11:15","Auditorio","Coffee Break ☕",None,False,True,None),
    ("AUD-05","11:15","12:00","Auditorio","Direct Lake en OneLake: descubre qué ocurre detrás de la magia","Nelson Lopez & Diana Aguilera",True,False,"OneLake & Storage"),
    ("AUD-06","12:00","12:45","Auditorio","El riesgo no está en la IA, está en tus datos","Elías Menchón & Jorge Fernández",True,False,"Seguridad"),
    ("AUD-07","12:45","13:30","Auditorio","Creando Modelos semánticos en la era de la IA","Miguel Egea",True,False,"Power BI & Modelos"),
    ("AUD-08","13:30","13:50","Auditorio","Kahoot Infiltrado",None,False,False,None),
    ("AUD-09","13:50","14:00","Auditorio","Despedida y cierre del evento",None,False,False,None),
    ("POL-01","08:30","09:00","Polivalente","Acreditaciones y café ☕",None,False,True,None),
    ("POL-02","09:00","09:15","Polivalente","Bienvenida y presentación",None,False,False,None),
    ("POL-03","09:15","10:00","Polivalente","SQL DB in Fabric: ¿cuánto tiene de Fabric y cuánto de SQL?","Roberto Carrancio",True,False,"Bases de Datos"),
    ("POL-04","10:00","10:45","Polivalente","Agentes Fabric + Copilot Studio: construyendo inteligencia aplicada","Antonio Torres",True,False,"IA & Agentes"),
    ("POL-05","10:45","11:15","Polivalente","Coffee Break ☕",None,False,True,None),
    ("POL-06","11:15","12:00","Polivalente","Solo sé que no sé si copiar: shortcuts vs mirroring en MS Fabric","Javier Buendía",True,False,"OneLake & Storage"),
    ("POL-07","12:00","12:45","Polivalente","Fabric sin dramas: Cómo dejar de rezar cada vez que subes a Producción","Kilian Baccaro & Oliver Bernabeu",True,False,"CI/CD & DevOps"),
    ("POL-08","12:45","13:30","Polivalente","Creando Modelos semánticos en la era de la IA","Miguel Egea",True,False,"Power BI & Modelos"),
    ("POL-09","13:30","13:50","Polivalente","Kahoot Infiltrado",None,False,False,None),
    ("POL-10","13:50","14:00","Polivalente","Despedida y cierre del evento",None,False,False,None),
]

schema = StructType([
    StructField("talk_id",    StringType(),  False),
    StructField("start_time", StringType(),  True),
    StructField("end_time",   StringType(),  True),
    StructField("room",       StringType(),  True),
    StructField("title",      StringType(),  True),
    StructField("speaker",    StringType(),  True),
    StructField("is_talk",    BooleanType(), True),
    StructField("is_break",   BooleanType(), True),
    StructField("track",      StringType(),  True),
])

df_raw = spark.createDataFrame(talks_data, schema=schema)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

df_enriched = (
    df_raw
    .withColumn("duration_min",
        (col("end_time").substr(1,2).cast(IntegerType()) * 60
         + col("end_time").substr(4,2).cast(IntegerType()))
      - (col("start_time").substr(1,2).cast(IntegerType()) * 60
         + col("start_time").substr(4,2).cast(IntegerType()))
    )
    .withColumn("speaker_count",
        when(col("speaker").isNull(), lit(0))
        .when(col("speaker").contains("&"), lit(2))
        .otherwise(lit(1))
    )
    .withColumn("event_date",  lit(str(date(2026, 6, 13))))
    .withColumn("loaded_env",  lit(FABRIC_ENV))
    .withColumn("loaded_at",   current_timestamp())
)

df_enriched.write.format("delta").mode("overwrite").option("overwriteSchema","true").saveAsTable(RAW_TABLE_NAME)
print(f"[{FABRIC_ENV}] ✅ Tabla '{RAW_TABLE_NAME}' escrita — {df_enriched.count()} registros.")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
