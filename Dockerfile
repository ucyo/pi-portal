# Pi Portal - Backend Dockerfile
# Multi-stage build for smaller final image

# Build stage
FROM python:3.12-slim AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml .
COPY README.md .

# Install dependencies
RUN uv sync --frozen --no-dev

# Production stage
FROM python:3.12-slim

# Install Node.js (required for Pi)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g @mariozechner/pi-coding-agent \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 piportal && \
    mkdir -p /app /data/pi_sessions && \
    chown -R piportal:piportal /app /data

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY --chown=piportal:piportal backend/ ./backend/
COPY --chown=piportal:piportal frontend/ ./frontend/
COPY --chown=piportal:piportal config/ ./config/
COPY --chown=piportal:piportal pyproject.toml .
COPY --chown=piportal:piportal README.md .

# Switch to non-root user
USER piportal

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app" \
    PI_PORTAL_SERVER_HOST=0.0.0.0 \
    PI_PORTAL_SERVER_PORT=8000 \
    PI_PORTAL_PI_SESSION_DIR=/data/pi_sessions \
    PI_PORTAL_PI_EXECUTABLE=/usr/bin/pi

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()"

# Run the application
CMD ["python", "-m", "backend.server"]
