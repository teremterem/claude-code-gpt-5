# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python project that creates a LiteLLM proxy server to connect Anthropic's Claude Code CLI with OpenAI's GPT-5 models. The proxy intercepts Claude Code requests and routes them to GPT-5 variants with different reasoning effort levels.

## Common Commands

### Development Setup
```bash
# Install dependencies and setup environment
uv sync

# Install with optional dependencies
uv sync --extra langfuse  # For Langfuse logging integration
uv sync --all-extras      # Install all optional dependencies
uv sync --extra dev       # Install development dependencies
```

### Running the Server
```bash
# Start the LiteLLM proxy server
uv run litellm --config config.yaml

# Run with specific environment file
uv run litellm --config config.yaml
```

### Code Quality
```bash
# Format code with Black (line length: 119)
uv run black .
uv run black --check .  # Check formatting without changing files

# Run pylint for linting
uv run pylint proxy/

# Run pre-commit hooks
uv run pre-commit run --all-files
```

## Architecture

### Core Components

**proxy/custom_llm_router.py** - Main routing logic
- `CustomLLMRouter` class extends LiteLLM's CustomLLM
- Handles sync/async completion, streaming requests
- Adds OpenAI-specific message modifications for tool call limitations
- Routes requests through `route_model()` function

**proxy/route_model.py** - Model routing and resolution
- `route_model()` - Main routing function that maps requested models to provider models
- `resolve_model_for_provider()` - Handles GPT-5 reasoning effort aliases (e.g., `gpt-5-reason-medium`)
- Supports Claude model remapping via environment variables
- Extracts reasoning effort parameters from model names

**proxy/config.py** - Configuration management
- Environment variable handling for model remapping
- Langfuse logging integration setup
- OpenAI tool call enforcement configuration

**proxy/convert_stream.py** - Stream processing
- Converts LiteLLM streaming chunks to GenericStreamingChunk format
- Handles tool call streaming for different providers

### Model Routing Logic

The proxy supports these model patterns:
- **GPT-5 variants**: `gpt-5`, `gpt-5-mini`, `gpt-5-nano`
- **Reasoning levels**: `-reason-minimal`, `-reason-low`, `-reason-medium`, `-reason-high`
- **Claude remapping**: Environment variables can redirect Claude models to other providers

Example: `gpt-5-reason-medium` → `openai/gpt-5` with `{"reasoning_effort": "medium"}`

### Environment Configuration

Key environment variables (configured in `.env`):
- `OPENAI_API_KEY` - Required for GPT-5 access
- `ANTHROPIC_API_KEY` - Required for Claude Code fast model
- `REMAP_CLAUDE_SONNET_TO` - Redirect Sonnet requests to different model
- `REMAP_CLAUDE_HAIKU_TO` - Redirect Haiku requests to different model
- `REMAP_CLAUDE_OPUS_TO` - Redirect Opus requests to different model
- `OPENAI_ENFORCE_ONE_TOOL_CALL_PER_RESPONSE` - Limits OpenAI to single tool calls
- `LANGFUSE_SECRET_KEY`, `LANGFUSE_PUBLIC_KEY` - Optional Langfuse logging

## Configuration Files

- **config.yaml** - LiteLLM proxy configuration that routes all models through custom handler
- **pyproject.toml** - Python project configuration with dependencies and Black settings
- **.pre-commit-config.yaml** - Pre-commit hooks for code quality (trailing whitespace, Black, Pylint)
