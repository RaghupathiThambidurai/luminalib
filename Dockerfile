# Multi-stage build for Python Backend
FROM python:3.11-slim as base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Development stage
FROM base as development

ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=development
ENV DEBUG=True

# Copy entire app
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production stage
FROM base as production

ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=production
ENV DEBUG=False

# Create non-root user
RUN useradd -m -u 1000 appuser

# Copy app
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
