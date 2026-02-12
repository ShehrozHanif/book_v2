FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (bust cache on every deploy)
COPY src/ ./src/

# Create logs directory
RUN mkdir -p logs

# Expose port (Render sets PORT dynamically)
EXPOSE ${PORT:-8000}

# Run application (use shell form so $PORT is expanded at runtime)
CMD uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}
