# Python Mastery Hub - Production Docker Image
# Multi-stage build for optimized production deployment

# Build stage - includes development tools for building
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies required for building
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry==1.7.1

# Configure Poetry
ENV POETRY_NO_INTERACTION=1
ENV POETRY_VENV_IN_PROJECT=1
ENV POETRY_CACHE_DIR=/tmp/poetry_cache

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --only=main && rm -rf $POETRY_CACHE_DIR

# Production stage - minimal runtime image
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PATH="/app/.venv/bin:$PATH"

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Copy virtual environment from builder stage
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY src/ ./src/
COPY README.md ./

# Copy static files for web interface
COPY src/python_mastery_hub/web/static ./static
COPY src/python_mastery_hub/web/templates ./templates

# Change ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port for web interface
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command - can be overridden
CMD ["python", "-m", "python_mastery_hub.web.app"]

# Development stage - includes development tools
FROM builder as development

# Install development dependencies
RUN poetry install

# Install additional development tools
RUN apt-get update && apt-get install -y \
    vim \
    nano \
    htop \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy all files including tests
COPY . .

# Don't switch to non-root user in development
WORKDIR /app

# Expose port for web interface and additional ports for debugging
EXPOSE 8000 5678

# Default command for development
CMD ["python", "-m", "python_mastery_hub.web.app"]

# CLI stage - optimized for command-line usage
FROM production as cli

# Override default command for CLI
CMD ["python", "-m", "python_mastery_hub.cli.main", "--help"]

# Test stage - includes testing dependencies
FROM development as test

# Install test dependencies
RUN poetry install --with dev

# Copy test files
COPY tests/ ./tests/

# Run tests by default
CMD ["pytest", "tests/", "-v"]