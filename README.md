# PDF Document Processing with pgvector

This project processes PDF documents, generates embeddings using Ollama, and stores them in PostgreSQL (AWS RDS) with pgvector for semantic search capabilities.

## Prerequisites

- Docker and Docker Compose
- Python 3.10 or higher
- Git
- AWS Account (for RDS PostgreSQL with pgvector)

## Project Structure

```
.
├── data/
│   ├── input/          # Place your PDF files here
│   ├── output/         # Generated Iceberg tables and JSONL files
│   └── answers/        # Query results
├── scripts/
│   └── run_process.sh  # Script to run the entire process
├── src/
│   ├── helpers.py      # Helper functions
│   ├── main.py         # Main processing logic
│   └── queries.py      # Predefined queries
├── terraform/          # Infrastructure as Code
│   └── rds.tf         # RDS and pgvector configuration
├── Dockerfile
├── docker-compose.yml
├── .env.example        # Example environment variables
└── pyproject.toml
```

## Setup Steps

### 1. Infrastructure Setup

1. Initialize Terraform:

   ```bash
   cd terraform
   terraform init
   ```

2. Apply the configuration:
   ```bash
   terraform apply
   ```

This will:

- Create an RDS PostgreSQL instance
- Configure the pgvector extension
- Set up necessary security groups and networking

After Terraform completes, it will output the RDS connection details including:

- Database host
- Port
- Database name
- Username
- Password

### 2. Environment Configuration

1. Copy the example environment file:

   ```bash
   cp .env.example .env
   ```

2. Update the `.env` file with the RDS connection details from the Terraform output:
   ```env
   POSTGRES_HOST=<rds_host_from_terraform>
   POSTGRES_PORT=<rds_port_from_terraform>
   POSTGRES_DB=<db_name_from_terraform>
   POSTGRES_USER=<username_from_terraform>
   POSTGRES_PASSWORD=<password_from_terraform>
   ```

⚠️ Important: The application will not work correctly until you've configured the `.env` file with the RDS connection details.

## Running the Project

### Quick Start

1. Place your PDF file in the `data/input` directory
2. Make the run script executable:
   ```bash
   chmod +x scripts/run_process.sh
   ```
3. Run the process:
   ```bash
   ./scripts/run_process.sh
   ```

The script will:

1. Build and start Docker containers
2. Pull the required Ollama model
3. Process the PDF and store embeddings in PostgreSQL
4. Run predefined queries
5. Save results in `data/answers/answers.jsonl`

### Manual Steps

If you prefer to run steps manually:

1. Start the containers:

   ```bash
   docker compose up -d --build
   ```

2. Pull the Ollama model:

   ```bash
   docker exec ollama ollama pull nomic-embed-text
   ```

3. Run the process:

   ```bash
   docker exec -it app python -m src.main
   ```

4. Stop the containers when done:
   ```bash
   docker compose down
   ```

## Output Files

- `data/output/table/`: Spark Iceberg table with processed data
- `data/output/jsonl_file/`: JSONL file with processed data
- `data/answers/answers.jsonl`: Query results with similarity scores

## Querying

The project includes predefined queries in `src/queries.py`. Each query:

1. Is converted to an embedding using the same model as documents
2. Is compared against document embeddings using cosine similarity
3. Returns the top 3 most similar document chunks

## Recent Improvements

- Added proper pgvector extension setup in RDS
- Improved SQLAlchemy transaction handling
- Enhanced type hints for better code maintainability
- Added infrastructure as code with Terraform

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
