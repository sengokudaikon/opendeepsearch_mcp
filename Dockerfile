# Dockerfile for OpenDeepSearch MCP Server
FROM python:3.10-bookworm AS builder

WORKDIR /app

# Install UV and create virtual environment
RUN pip install uv==0.2.5 && \
    uv venv -n .venv

# Copy all necessary files first
COPY pyproject.toml README.md ./
COPY src ./src

# Generate lock file and install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    . .venv/bin/activate && \
    uv pip compile pyproject.toml -o uv.lock && \
    uv pip install --no-deps -r uv.lock && \
    uv pip install --no-deps -e .

# Final stage
FROM python:3.10-slim-bookworm
WORKDIR /app

# Copy virtual environment and source code from builder
COPY --from=builder /app/.venv ./.venv
COPY --from=builder /app/src ./src

# Ensure scripts from .venv/bin are in PATH
ENV PATH="/app/.venv/bin:$PATH"

# Install necessary system dependencies for PyTorch and other libraries
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Verify package discovery
RUN .venv/bin/python -c "import sys; print(sys.path)"

# Ensure unbuffered stdio
ENV PYTHONUNBUFFERED=1
ENV PYTHONFAULTHANDLER=1

# Add logging level control
ENV LOG_LEVEL=INFO

# Run as non-root user
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Use the correct entry point for our package
ENTRYPOINT ["opendeepsearch-mcp"]
