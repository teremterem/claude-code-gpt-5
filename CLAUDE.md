# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository provides a LiteLLM proxy that allows Claude Code to use GPT-5 models as the "smart" model while keeping Claude models for fast operations. It routes model requests through a custom handler that maps friendly aliases to provider models with specific parameters.

## Key Architecture

- **Custom LLM Router** (`proxy/custom_llm_router.py`): Core routing logic that handles both sync/async completion and streaming
- **Model Routing** (`proxy/route_model.py`): Maps model aliases like `gpt-5-reason-medium` to `openai/gpt-5` with reasoning_effort parameters
- **Stream Conversion** (`proxy/convert_stream.py`): Converts provider-specific streaming chunks to generic format

## Development Commands

### Setup and Run Server
```bash
# Copy environment template
cp .env.template .env

# Install dependencies (requires uv)
uv sync

# Start the LiteLLM proxy server
uv run litellm --config config.yaml
```

### Code Quality Tools
```bash
# Format Python code
uv run black .

# Lint Python code
uv run pylint proxy/

# Install pre-commit hooks
uv run pre-commit install
```

### Available GPT-5 Models
The proxy supports these model aliases:
- `gpt-5-reason-minimal/low/medium/high`
- `gpt-5-mini-reason-minimal/low/medium/high`
- `gpt-5-nano-reason-minimal/low/medium/high`

Claude models pass through as `anthropic/claude-*`.

## Environment Configuration

Required environment variables in `.env`:
- `OPENAI_API_KEY`: For GPT-5 models
- `ANTHROPIC_API_KEY`: For Claude fast model (still required)

Optional:
- `GPT_ENFORCE_ONE_TOOL_CALL_PER_RESPONSE=true` (recommended for Claude Code compatibility)
- Langfuse keys for request/response logging

## Known Issues

- Web Search tool doesn't work with GPT-5 models due to schema incompatibility
- Use Claude models (`/model claude-3-5-sonnet-20241022`) as workaround for web search
- Fetch tool works normally with all models

## Testing with Claude Code

Start the proxy and connect Claude Code:
```bash
ANTHROPIC_BASE_URL=http://localhost:4000 claude --model gpt-5-reason-medium
```
