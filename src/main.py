from .helpers import (
    process_document,
    deduplicate_data,
    create_dataframe,
    create_iceberg_table,
    prepare_queries,
    store_in_postgres,
    save_json_data,
    spark,
)

from .constants import QUERIES, ANSWERS_PATH, SPARK_DB, SPARK_TBL_NAME


def main() -> None:
    """Process PDF, transform data, store in PostgreSQL, and run queries."""
    ids, chunks, metadatas, embeddings, model = process_document()
    print("✅ IDs, chunks, metadatas, embeddings and model generated")

    df = create_dataframe(ids, chunks, metadatas, embeddings)
    print("✅ DataFrame created")

    create_iceberg_table(df)
    print("✅ Saved Iceberg table to S3")

    # Load DataFrame from Iceberg table
    df_loaded = spark.table(f"{SPARK_DB}.{SPARK_TBL_NAME}")
    print("✅ DataFrame loaded")
    print("Number of rows in DataFrame:", df_loaded.count())

    df_deduplicated = deduplicate_data(df_loaded)
    print("✅ DataFrame deduplicated")

    # Store in PostgreSQL using LangChain's PGVector
    store_in_postgres(df_deduplicated, model)

    answers = prepare_queries(QUERIES, model)
    print("✅ Answers prepared")

    save_json_data(answers, ANSWERS_PATH)
    print(f"✅ Answers Saved in {ANSWERS_PATH}")
    print("✅ Process completed!")

    spark.stop()
    print("✅ Spark session stopped.")


if __name__ == "__main__":
    main()
