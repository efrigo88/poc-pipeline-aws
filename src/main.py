import os
from typing import List, Dict, Any, Tuple

from langchain_ollama import OllamaEmbeddings

from .helpers import (
    parse_pdf,
    get_text_content,
    get_chunks,
    get_ids,
    get_metadata,
    get_embeddings,
    deduplicate_data,
    create_dataframe,
    create_iceberg_table,
    prepare_queries,
    store_in_postgres,
    save_json_data,
    spark,
)

from .queries import QUERIES


SPARK_TABLE_NAME = "documents"
BUCKET_NAME = os.getenv("S3_BUCKET")
SPARK_BUCKET_NAME = BUCKET_NAME.replace("s3://", "s3a://")
INPUT_PATH = f"s3://{BUCKET_NAME}/data/input/Example_DCL.pdf"
OUTPUT_PATH = f"{SPARK_BUCKET_NAME}/data/output/"
ANSWERS_PATH = f"{SPARK_BUCKET_NAME}/data/answers/answers.jsonl"
CHUNK_SIZE = 200
CHUNK_OVERLAP = 20


def process_document() -> Tuple[
    List[str],
    List[str],
    List[Dict[str, Any]],
    List[List[float]],
    OllamaEmbeddings,
]:
    """Process PDF and generate embeddings."""
    doc = parse_pdf(INPUT_PATH)
    text_content = get_text_content(doc)
    print("✅ Text content generated.")

    chunks = get_chunks(text_content, CHUNK_SIZE)
    ids = get_ids(chunks, INPUT_PATH)
    metadatas = get_metadata(chunks, doc, INPUT_PATH)
    print("✅ Chunks, IDs and Metadatas generated.")

    model = OllamaEmbeddings(
        model="nomic-embed-text", base_url=os.getenv("OLLAMA_HOST")
    )
    embeddings = get_embeddings(chunks, model)
    print("✅ Embeddings generated.")
    return ids, chunks, metadatas, embeddings, model


def main() -> None:
    """Process PDF, transform data, store in PostgreSQL, and run queries."""
    # Process document and generate embeddings
    ids, chunks, metadatas, embeddings, model = process_document()

    df = create_dataframe(ids, chunks, metadatas, embeddings)

    create_iceberg_table(df, SPARK_TABLE_NAME)

    # Load DataFrame from Iceberg table
    df_loaded = spark.table(SPARK_TABLE_NAME)

    df_deduplicated = deduplicate_data(df_loaded)
    print(f"✅ Deduplicated DataFrame in {SPARK_TABLE_NAME}")

    # Store in PostgreSQL using LangChain's PGVector
    store_in_postgres(df_deduplicated, model)

    # Run queries and save answers
    answers = prepare_queries(QUERIES, model)
    save_json_data(answers, ANSWERS_PATH)
    print(f"✅ Saved answers in {ANSWERS_PATH}")
    print("✅ Process completed!")

    spark.stop()
    print("✅ Spark session stopped.")


if __name__ == "__main__":
    main()
