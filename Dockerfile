# Use Python 3.11 slim image for amd64
FROM --platform=linux/amd64 python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy project files
COPY . .

# Install Python dependencies using uv
RUN uv sync --frozen

# Create .env template if it doesn't exist
RUN if [ ! -f .env ]; then \
    echo "OPENAI_API_KEY=" > .env && \
    echo "ANTHROPIC_API_KEY=" >> .env && \
    echo "OPENAI_ENFORCE_ONE_TOOL_CALL_PER_RESPONSE=true" >> .env; \
    fi

# Expose port 4000 (default LiteLLM proxy port)
EXPOSE 4000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:4000/health || exit 1

# Default command to run the LiteLLM proxy
CMD ["uv", "run", "litellm", "--config", "config.yaml", "--port", "4000", "--host", "0.0.0.0"]
