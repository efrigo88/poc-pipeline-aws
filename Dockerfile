FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    procps \
    libpq-dev \
    gcc \
    python3-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy only dependency definition first for better layer caching
COPY pyproject.toml .

# Install dependencies using uv without virtual environment
RUN uv pip install --system --no-cache-dir -e . && rm -rf ~/.cache

# Copy the rest of the application
COPY . .

# The command to run your script
CMD ["python", "-m", "src.main"]
