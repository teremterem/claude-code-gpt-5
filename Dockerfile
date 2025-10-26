FROM python:3.13-slim

LABEL org.opencontainers.image.source=https://github.com/teremterem/claude-code-gpt-5 \
      org.opencontainers.image.description="Connect Claude Code CLI to GPT-5" \
      org.opencontainers.image.licenses=MIT

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

# Copy all the project files
COPY . .

# Expose port 4000 (default LiteLLM server port)
EXPOSE 4000

# # !!! WARNING !!!
# # LiteLLM's /health endpoint also checks the responsiveness of the deployed
# # Language Models, which incurs extra costs !!! Uncomment the lines below
# # only if you're comfortable with these extra costs !!!

# HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
#    CMD curl -f -H "Authorization: Bearer ${LITELLM_MASTER_KEY}" http://localhost:4000/health || exit 1

# Default command to run the LiteLLM server
CMD ["uv", "run", "litellm", "--config", "config.yaml", "--port", "4000", "--host", "0.0.0.0"]
