import os
import pyspark.sql.types as T

SPARK_DB = "poc_pipeline"
SPARK_TBL_NAME = "documents"

BUCKET_NAME = os.getenv("S3_BUCKET")
SPARK_BUCKET_NAME = BUCKET_NAME.replace("s3://", "s3a://")
INPUT_PATH = f"s3://{BUCKET_NAME}/data/input/Example_DCL.pdf"
ANSWERS_PATH = f"s3://{SPARK_BUCKET_NAME}/data/answers/answers.jsonl"

CHUNK_SIZE = 200
CHUNK_OVERLAP = 20

SCHEMA = T.StructType(
    [
        T.StructField("id", T.StringType(), True),
        T.StructField("chunk", T.StringType(), True),
        T.StructField(
            "metadata",
            T.StructType(
                [
                    T.StructField("source", T.StringType(), True),
                    T.StructField("chunk_index", T.IntegerType(), True),
                    T.StructField("title", T.StringType(), True),
                    T.StructField("chunk_size", T.IntegerType(), True),
                ]
            ),
            True,
        ),
        T.StructField("processed_at", T.TimestampType(), True),
        T.StructField("processed_dt", T.StringType(), True),
        T.StructField("embeddings", T.ArrayType(T.FloatType()), True),
    ]
)

# Queries to be used for the application
QUERIES = [
    "¿Cuándo y cómo comenzó la relación entre la declarante y su pareja?",
    "¿Qué tipo de abusos sufrió la persona declarante?",
    "¿Cuáles fueron los incidentes más graves de abuso?",
    "¿Hubo abuso económico o control del dinero? ¿Cómo era?",
    "¿Cómo afectó el abuso a la salud mental de la declarante?",
    "¿Qué sentimientos experimentaba la declarante durante la relación?",
    "¿La declarante buscó ayuda psicológica? ¿Por qué sí o por qué no?",
    "¿Cómo era la relación entre la pareja abusiva y los hijos?",
    "¿Por qué la declarante solicita el amparo bajo VAWA?",
    "¿Qué riesgos correría la declarante si fuera deportada?",
]
