# ========== MULTI-STAGE DOCKERFILE FOR FASTAPI RAG APPLICATION ==========
# Stage 1: Base image with Python and dependencies
# Alternative: Use python:3.11-slim if 3.12 has issues

FROM python:3.11-slim as base       

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*



# Copy application code (new modular structure)
# Copy the entire app package
COPY app/ ./app/
COPY run.py .
COPY .env .

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download sentence-transformers model to cache it
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-mpnet-base-v2')"

# Expose port for FastAPI
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application using new modular structure
# Using app.main:app instead of app_fastapi:app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
