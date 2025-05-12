import os
from datetime import datetime

ingestion_dt = datetime.now().strftime("%Y-%m-%d")
BUCKET_NAME = os.getenv("S3_BUCKET")
INPUT_PATH = f"s3://{BUCKET_NAME}/data/input/Example_DCL.pdf"
OUTPUT_PATH = f"s3://{BUCKET_NAME}/data/output/{ingestion_dt}"
ANSWERS_PATH = f"s3://{BUCKET_NAME}/data/answers/answers.jsonl"

CHUNK_SIZE = 200
CHUNK_OVERLAP = 20

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
