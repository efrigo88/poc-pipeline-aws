import pandas as pd

from .helpers import (
    process_document,
    deduplicate_data,
    create_dataframe,
    prepare_queries,
    store_in_postgres,
    save_json_data,
)

from .constants import QUERIES, ANSWERS_PATH, OUTPUT_PATH


def main() -> None:
    """Process PDF, transform data, store in PostgreSQL, and run queries."""
    ids, chunks, metadatas, embeddings, model = process_document()
    print("✅ IDs, chunks, metadatas, embeddings and model generated")

    df = create_dataframe(ids, chunks, metadatas, embeddings)
    print("✅ DataFrame created")

    # Save DataFrame to S3
    df.to_parquet(f"{OUTPUT_PATH}/data.parquet")
    print("✅ Saved table to S3")

    # Load DataFrame from S3
    df_loaded = pd.read_parquet(f"{OUTPUT_PATH}/data.parquet")
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


if __name__ == "__main__":
    main()
