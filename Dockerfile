FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

COPY .python-version ./
COPY uv.lock ./
COPY pyproject.toml ./

# Install Python dependencies using uv (before copying other project files,
# so this layer is rebuilt less often during development)
RUN uv sync --frozen

# Set up the environment variable defaults
COPY .env.template .env

# Copy all the project files
COPY . .

# Expose port 4000 (default LiteLLM proxy port)
EXPOSE 4000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:4000/health || exit 1

# Default command to run the LiteLLM proxy
CMD ["uv", "run", "litellm", "--config", "config.yaml", "--port", "4000", "--host", "0.0.0.0"]
