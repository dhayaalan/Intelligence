# ==============================================================================
# Sential Intelligence Platform - Backend Dockerfile
# Production-ready, non-root user, healthchecked container for FastAPI core
# ==============================================================================

FROM python:3.10-slim

# Prevent Python from writing .pyc files and enable unbuffered streaming
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PORT=8000

WORKDIR /app

# Install minimal OS dependencies for network diagnostics and healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    dnsutils \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

# Create non-root system user and group
RUN groupadd -r sential && useradd -r -g sential -d /app -s /sbin/nologin sential

# Install Python dependencies reproducibly
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend application source
COPY . .

# Set ownership to non-root user
RUN chown -R sential:sential /app

# Switch to non-root execution
USER sential

# Expose internal API port
EXPOSE 8000

# Container healthcheck: verify process and API responsiveness
HEALTHCHECK --interval=15s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start FastAPI application using ASGI server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
