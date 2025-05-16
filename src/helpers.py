import os
import json
from datetime import datetime
from typing import List, Dict, Any, BinaryIO, Tuple

import pandas as pd
import boto3
from botocore.exceptions import ClientError
from sqlalchemy import create_engine, text, Engine
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_postgres import PGVector
from docling.datamodel.document import InputDocument
from docling.document_converter import DocumentConverter
from langchain_ollama import OllamaEmbeddings

from .constants import INPUT_PATH, CHUNK_SIZE

# Initialize S3 client
s3_client = boto3.client("s3")


class S3Error(Exception):
    """Custom exception for S3-related errors."""


def create_dataframe(
    ids: List[str],
    chunks: List[str],
    metadatas: List[Dict[str, Any]],
    embeddings: List[List[float]],
) -> pd.DataFrame:
    """Create and save DataFrame with processed data."""
    df = pd.DataFrame(
        {
            "id": ids,
            "chunk": chunks,
            "metadata": metadatas,
            "processed_at": datetime.now(),
            "processed_dt": datetime.now().strftime("%Y-%m-%d"),
            "embeddings": embeddings,
        }
    )
    return df


def deduplicate_data(df: pd.DataFrame) -> pd.DataFrame:
    """Deduplicate data and return processed DataFrame."""
    df = (
        df.sort_values("processed_at", ascending=False)
        .groupby("id")
        .agg(
            {
                "processed_at": "first",
                "processed_dt": "first",
                "chunk": "first",
                "metadata": "first",
                "embeddings": "first",
            }
        )
        .reset_index()
    )
    return df


def get_s3_bucket_and_key(s3_path: str) -> tuple[str, str]:
    """Extract bucket name and key from S3 path."""
    if not (s3_path.startswith("s3://") or s3_path.startswith("s3a://")):
        raise ValueError(
            "Path must be an S3 path starting with 's3://' or 's3a://'"
        )
    path_without_prefix = (
        s3_path[5:] if s3_path.startswith("s3://") else s3_path[6:]
    )
    bucket_name = path_without_prefix.split("/")[0]
    key = "/".join(path_without_prefix.split("/")[1:])
    return bucket_name, key


def read_from_s3(s3_path: str) -> BinaryIO:
    """Read file from S3."""
    bucket_name, key = get_s3_bucket_and_key(s3_path)
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=key)
        return response["Body"]
    except ClientError as e:
        raise S3Error(f"Error reading from S3: {str(e)}") from e


def write_to_s3(file_path: str, s3_path: str) -> None:
    """Write file to S3."""
    bucket_name, key = get_s3_bucket_and_key(s3_path)
    try:
        s3_client.upload_file(file_path, bucket_name, key)
    except ClientError as e:
        raise S3Error(f"Error writing to S3: {str(e)}") from e


def parse_document(source_path: str) -> InputDocument:
    """Parse the PDF document using DocumentConverter."""
    converter = DocumentConverter()
    s3_file = read_from_s3(source_path)
    temp_file = f"/tmp/{source_path.split('/')[-1]}"
    with open(temp_file, "wb") as f:
        f.write(s3_file.read())
    try:
        result = converter.convert(temp_file)
    finally:
        # Clean up temporary file
        if os.path.exists(temp_file):
            os.remove(temp_file)
    return result.document


def get_text_content(doc: InputDocument) -> List[str]:
    """Extract text content from the document."""
    return [
        text_item.text.strip()
        for text_item in doc.texts
        if text_item.text.strip() and text_item.label == "text"
    ]


def get_chunks(
    text_content: List[str], chunk_size: int = 750, chunk_overlap: int = 100
) -> List[str]:
    """Split text content into semantically meaningful chunks."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", "!", "?", " ", ""],
    )
    chunks = []
    for content in text_content:
        chunks.extend(splitter.split_text(content))
    if not chunks:
        raise ValueError("No text chunks found in the document.")
    return chunks


def get_ids(chunks: List[str], source_path: str) -> List[str]:
    """Generate unique IDs for each chunk."""
    filename = source_path.split("/")[-1]
    return [f"{filename}_chunk_{i}" for i in range(len(chunks))]


def get_metadata(
    chunks: List[str],
    doc: InputDocument,
    source_path: str,
) -> List[Dict[str, Any]]:
    """Generate metadata for each chunk."""
    filename = source_path.split("/")[-1]
    return [
        {
            "source": filename,
            "chunk_index": i,
            "title": doc.name,
            "chunk_size": len(chunk),
        }
        for i, chunk in enumerate(chunks)
    ]


def get_embeddings(
    chunks: List[str],
    model: OllamaEmbeddings,
) -> List[List[float]]:
    """Get embeddings for a list of chunks using Ollama embeddings."""
    return model.embed_documents(chunks)


def save_json_data(data: List[Dict[str, Any]], s3_path: str) -> None:
    """Save data to a JSONL file in S3 (one JSON object per line)."""
    # Create a temporary file
    temp_dir = "/tmp"
    os.makedirs(temp_dir, exist_ok=True)
    temp_file = os.path.join(temp_dir, os.path.basename(s3_path))

    # Write to temporary file
    with open(temp_file, "w", encoding="utf-8") as f:
        for item in data:
            json.dump(item, f, ensure_ascii=False)
            f.write("\n")

    # Upload to S3
    write_to_s3(temp_file, s3_path)

    # Clean up temporary file
    if os.path.exists(temp_file):
        os.remove(temp_file)


def get_db_connection_string() -> str:
    """Create a connection string for PostgreSQL."""
    return (
        f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:"
        f"{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:"
        f"{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
    )


def ensure_pgvector_extension_exists() -> None:
    """Ensure the pgvector extension is created in the database."""
    engine: Engine = create_engine(get_db_connection_string())
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))


def init_vector_store(embeddings: OllamaEmbeddings) -> PGVector:
    """Initialize the vector store with LangChain's PGVector."""
    connection_string = get_db_connection_string()
    collection_name = "documents"

    # Ensure pgvector extension exists before initializing PGVector
    ensure_pgvector_extension_exists()

    return PGVector(
        embeddings=embeddings,
        collection_name=collection_name,
        connection=connection_string,
        use_jsonb=True,
    )


def store_in_postgres(df: pd.DataFrame, embeddings: OllamaEmbeddings) -> None:
    """Store data in PostgreSQL using LangChain's PGVector."""
    vector_store: PGVector = init_vector_store(embeddings)

    # Convert DataFrame rows to LangChain Documents
    documents = []
    ids = []
    for _, row in df.iterrows():
        doc = Document(
            page_content=row["chunk"],
            metadata={
                "id": row["id"],
                "source": row["metadata"]["source"],
                "chunk_index": row["metadata"]["chunk_index"],
                "title": row["metadata"]["title"],
                "chunk_size": row["metadata"]["chunk_size"],
                "processed_at": row["processed_at"].isoformat(),
                "processed_dt": row["processed_dt"],
            },
        )
        documents.append(doc)
        ids.append(row["id"])

    # Add documents to vector store with upsert
    vector_store.add_documents(documents, ids=ids)
    print(f"📊 Total documents added to PostgreSQL: {len(documents)}")


def prepare_queries(
    queries: List[str],
    embeddings: OllamaEmbeddings,
) -> List[Dict[str, Any]]:
    """Run queries and prepare results in json format"""
    vector_store: PGVector = init_vector_store(embeddings)
    all_results = []

    for query in queries:
        # Perform similarity search using LangChain's PGVector
        results = vector_store.similarity_search(
            query,
            k=3,
        )

        query_result = {
            "processed_at": datetime.now().isoformat(),
            "query": query,
            "results": [
                {
                    "text": doc.page_content,
                    "metadata": doc.metadata,
                    "similarity": 1.0,
                }
                for doc in results
            ],
        }
        all_results.append(query_result)

    return all_results


def process_document() -> Tuple[
    List[str],
    List[str],
    List[Dict[str, Any]],
    List[List[float]],
    OllamaEmbeddings,
]:
    """Process PDF and generate embeddings."""
    doc = parse_document(INPUT_PATH)
    text_content = get_text_content(doc)
    chunks = get_chunks(text_content, CHUNK_SIZE)
    ids = get_ids(chunks, INPUT_PATH)
    metadatas = get_metadata(chunks, doc, INPUT_PATH)
    model = OllamaEmbeddings(
        model="nomic-embed-text", base_url=os.getenv("OLLAMA_HOST")
    )
    embeddings = get_embeddings(chunks, model)
    return ids, chunks, metadatas, embeddings, model
