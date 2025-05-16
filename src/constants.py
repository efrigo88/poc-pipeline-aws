import os
from datetime import datetime

ingestion_dt = datetime.now().strftime("%Y-%m-%d")
BUCKET_NAME = os.getenv("S3_BUCKET")
INPUT_PATH = f"s3://{BUCKET_NAME}/data/input/transcript.pdf"
OUTPUT_PATH = f"s3://{BUCKET_NAME}/data/output/{ingestion_dt}"
ANSWERS_PATH = f"s3://{BUCKET_NAME}/data/answers/answers.jsonl"

CHUNK_SIZE = 100
CHUNK_OVERLAP = 20

# Queries to be used for the application
QUERIES = [
    "¿Quien es juan perez?",
    "¿juan perez es un hombre?",
    "¿juan perez es violento?",
    "¿Que cosas hizo juan perez?",
]
