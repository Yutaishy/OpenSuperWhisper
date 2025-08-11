# OpenSuperWhisper Docker Image
# Lightweight single-stage build for faster deployment

FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    HOST=0.0.0.0 \
    PORT=8000 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies (minimal set)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set work directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements-docker.txt .
RUN pip install --no-cache-dir -r requirements-docker.txt

# Copy application code
COPY OpenSuperWhisper/ ./OpenSuperWhisper/
COPY web_server.py .

# Create necessary directories with proper permissions
RUN mkdir -p /app/logs /tmp/opensuperwhisper && \
    chown -R appuser:appuser /app /tmp/opensuperwhisper

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/ || exit 1

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "web_server.py"]