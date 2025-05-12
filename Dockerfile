FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install uv
RUN pip install uv

# Copy only dependency definition first for better layer caching
COPY pyproject.toml .

# Install dependencies using uv without virtual environment
RUN uv pip install --system -e . && rm -rf ~/.cache

# Copy the rest of the application
COPY . .

# The command to run your script
CMD ["python", "-m", "src.main"]
