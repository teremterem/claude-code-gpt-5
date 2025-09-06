# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

This repository provides a LiteLLM proxy that allows Claude Code CLI to use OpenAI's GPT-5 models as the "smart" model while keeping Claude for the fast model.

## Commands

### Development

```bash
# Install dependencies
uv sync

# Install with Langfuse integration (optional)
uv sync --extra langfuse

# Run the proxy server
uv run litellm --config config.yaml

# Format Python code
black proxy/

# Run linting
pylint proxy/
```

### Pre-commit hooks

```bash
# Install pre-commit hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

## Architecture

### Model Routing System

The proxy uses a custom LiteLLM handler that intercepts model requests and routes them:

1. **`proxy/custom_llm_router.py`**: Main router class that implements LiteLLM's CustomLLM interface
   - Handles sync/async completion and streaming
   - Integrates with Langfuse for logging when configured
   - Routes all requests through the `route_model` function

2. **`proxy/route_model.py`**: Model mapping logic
   - Maps GPT-5 variants with reasoning effort levels (e.g., `gpt-5-reason-medium` → `openai/gpt-5` with `reasoning_effort: medium`)
   - Passes through Claude models unchanged for the fast model
   - Supports patterns: `gpt-5(-mini|-nano)?-reason-(minimal|low|medium|high)` and `claude-*`

3. **`proxy/convert_stream.py`**: Stream conversion utilities for handling different response formats

### Configuration

- **`config.yaml`**: LiteLLM configuration that routes all models through the custom handler
- **`.env`**: Contains API keys for OpenAI and Anthropic (required)
- **`pyproject.toml`**: Python project configuration with dependencies

## Important Notes

- The proxy requires both OpenAI and Anthropic API keys because Claude Code uses two models
- Web Search tool doesn't work with GPT-5 models (use `/model` command to switch to Claude temporarily)
- Fetch tool for specific URLs works normally
- Uses Python 3.8.1+ with uv for dependency management
- Black formatter configured with 119 character line length
- Pre-commit hooks enforce code quality (trailing whitespace, EOF fixes, black, pylint)
