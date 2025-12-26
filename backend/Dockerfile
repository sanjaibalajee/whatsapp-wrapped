# WhatsApp Wrapped Backend Dockerfile
# Build from root: docker build -f backend/Dockerfile .
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libmagic1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy root-level files (dependencies + core package)
COPY pyproject.toml uv.lock* .python-version ./
COPY core/ ./core/

# Install dependencies from root pyproject.toml
RUN uv sync --frozen --no-dev --no-install-project 2>/dev/null || uv sync --no-dev --no-install-project

# Copy backend app
COPY backend/app ./backend/app
COPY backend/run.py backend/gunicorn.conf.py ./backend/

# Set environment
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app/backend

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Default command (can be overridden for celery worker)
CMD ["gunicorn", "--config", "gunicorn.conf.py", "run:app"]
