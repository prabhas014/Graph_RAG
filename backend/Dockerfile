FROM python:3.11-slim

WORKDIR /app

# Install system dependencies if any are needed by python-jose, chromadb, etc.
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Set environment variables for docker environment
ENV DATABASE_URL="sqlite:///./data/sql_app.db"
ENV CHROMA_PERSIST_DIRECTORY="./data/chroma_db"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
