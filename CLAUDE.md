# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository provides a LiteLLM proxy that allows using Anthropic's Claude Code CLI with OpenAI's GPT-5 models. The proxy intercepts model requests and routes them appropriately based on configuration.

## Development Commands

### Code Formatting and Linting
```bash
# Format code with Black (line-length 119)
uv run black proxy/

# Run pylint to check code quality
uv run pylint proxy/

# Run pre-commit hooks
uv run pre-commit run --all-files
```

### Running the Proxy Server
```bash
# Start the LiteLLM proxy server
uv run litellm --config config.yaml

# The proxy runs on http://localhost:4000 by default
```

### Dependency Management
```bash
# Install dependencies
uv sync

# Install with Langfuse support for logging
uv sync --extra langfuse

# Install development dependencies
uv sync --extra dev
```

## Architecture

### Core Components

1. **Custom LLM Router** (`proxy/custom_llm_router.py`):
   - Routes incoming model requests to the appropriate provider (Anthropic or OpenAI)
   - Handles model name remapping based on environment configuration
   - Enforces single tool call per response for OpenAI models when `OPENAI_ENFORCE_ONE_TOOL_CALL_PER_RESPONSE=true`

2. **Model Routing** (`proxy/route_model.py`):
   - Maps Claude model names to configured alternatives (GPT-5 variants)
   - Handles reasoning effort aliases (e.g., `gpt-5-reason-medium`)
   - Prepends provider prefixes (`anthropic/` or `openai/`)

3. **Configuration** (`proxy/config.py`):
   - Reads environment variables for API keys and model remapping
   - Key variables:
     - `REMAP_CLAUDE_HAIKU_TO`: Remap Haiku models
     - `REMAP_CLAUDE_SONNET_TO`: Remap Sonnet models (default: gpt-5-reason-medium)
     - `REMAP_CLAUDE_OPUS_TO`: Remap Opus models (default: gpt-5-reason-high)
     - `MODEL_FOR_WEB_SEARCH`: Model used for web search operations
     - `OPENAI_ENFORCE_ONE_TOOL_CALL_PER_RESPONSE`: Ensures compatibility with Claude Code CLI

4. **Stream Conversion** (`proxy/convert_stream.py`):
   - Converts streaming responses to generic format for consistent handling

## Model Naming Convention

The proxy supports special reasoning effort aliases for GPT-5 models:
- Pattern: `{model-name}-reason-{effort}`
- Effort levels: `minimal`, `low`, `medium`, `high`
- Examples:
  - `gpt-5-reason-medium` → `openai/gpt-5` with `reasoning_effort: medium`
  - `gpt-5-mini-reason-low` → `openai/gpt-5-mini` with `reasoning_effort: low`

## Environment Configuration

Required environment variables in `.env`:
- `OPENAI_API_KEY`: OpenAI API key
- `ANTHROPIC_API_KEY`: Anthropic API key (still needed for fast model operations)

Optional configuration:
- `LANGFUSE_SECRET_KEY`, `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_HOST`: For request/response logging
- `OPENAI_BASE_URL`, `ANTHROPIC_BASE_URL`: Custom API endpoints

## Testing Considerations

When testing model routing and proxy functionality:
1. Verify environment variables are properly loaded
2. Check that model remapping works as expected
3. Ensure streaming responses are handled correctly
4. Test tool call enforcement for OpenAI models
