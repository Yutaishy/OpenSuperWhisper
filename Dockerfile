# OpenSuperWhisper Docker Image
# Multi-architecture support with optimized multi-stage build

# Build stage
FROM --platform=$BUILDPLATFORM python:3.12-slim AS builder

# Build arguments for multi-arch support
ARG TARGETPLATFORM
ARG BUILDPLATFORM
ARG TARGETOS
ARG TARGETARCH

# Set environment variables for build
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install requirements
COPY requirements-docker.txt /tmp/
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r /tmp/requirements-docker.txt

# Runtime stage
FROM --platform=$TARGETPLATFORM python:3.12-slim

# Labels for container metadata
LABEL org.opencontainers.image.title="OpenSuperWhisper" \
      org.opencontainers.image.description="Voice transcription service with real-time capabilities" \
      org.opencontainers.image.vendor="OpenSuperWhisper" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.source="https://github.com/yourusername/opensuperwhisper"

# Runtime environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    HOST=0.0.0.0 \
    PORT=8000 \
    WORKERS=4 \
    DEBIAN_FRONTEND=noninteractive \
    PYTHONPATH=/app:$PYTHONPATH

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    ffmpeg \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd -r -g 1000 appuser && \
    useradd -r -u 1000 -g appuser -d /app -s /sbin/nologin appuser

# Set work directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder --chown=appuser:appuser /opt/venv /opt/venv

# Copy application code
COPY --chown=appuser:appuser src/OpenSuperWhisper/ ./OpenSuperWhisper/
COPY --chown=appuser:appuser src/web_server.py .
COPY --chown=appuser:appuser src/run_app.py .
# configs directory is optional - uncomment if you have configuration files
# COPY --chown=appuser:appuser configs/ ./configs/

# Create necessary directories with proper permissions
RUN mkdir -p /app/logs /app/cache /tmp/opensuperwhisper && \
    chown -R appuser:appuser /app /tmp/opensuperwhisper && \
    chmod 755 /app && \
    chmod 755 /app/logs && \
    chmod 755 /app/cache

# Security: Drop all capabilities
USER appuser

# Health check with timeout
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Expose port (documentation only)
EXPOSE 8000

# Use exec form to ensure proper signal handling
ENTRYPOINT ["python"]
CMD ["-u", "web_server.py"]