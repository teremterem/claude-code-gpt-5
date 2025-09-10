# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Claude Code GPT-5 is a Python-based proxy service that enables using OpenAI's GPT-5 as the "smart" model in Anthropic's Claude Code CLI. It implements a custom LiteLLM proxy that routes requests between Claude Code and GPT-5.

## Development Commands

```bash
# Start the proxy server
uv run litellm --config config.yaml

# Install dependencies
uv sync --extra langfuse    # With Langfuse logging support
uv sync --all-extras        # All optional dependencies
uv sync --extra dev         # Development dependencies

# Code formatting and linting
uv run black .              # Format all Python files
uv run pylint proxy/        # Lint the proxy module

# Dependency management
uv lock                     # Update lock file
uv lock --upgrade          # Upgrade all dependencies
```

## Architecture

The proxy uses a custom router pattern with these core components:

- **proxy/custom_llm_router.py**: Main router implementing LiteLLM's CustomLLM interface for handling sync/async completions and streaming
- **proxy/route_model.py**: Model mapping logic that converts Claude model names to GPT-5 variants with reasoning effort levels
- **proxy/convert_stream.py**: Stream normalization between different provider formats
- **proxy/config.py**: Environment configuration and optional Langfuse integration

## Model Routing

The proxy remaps Claude models to GPT-5 variants based on environment variables:
- Claude Sonnet → GPT-5 reason-medium (configurable via REMAP_CLAUDE_SONNET_TO)
- Claude Opus → GPT-5 reason-high (configurable via REMAP_CLAUDE_OPUS_TO)
- Web search uses claude-sonnet-4 (configurable via MODEL_FOR_WEB_SEARCH)

## Code Standards

- Python 3.8.1+ compatibility required
- Black formatting with 119 character line length
- Pylint compliance enforced via pre-commit hooks
- Always use `raise X from Y` for exception chaining
- Run black and pylint after any Python file modifications

## Environment Setup

1. Copy `.env.template` to `.env`
2. Set OPENAI_API_KEY and ANTHROPIC_API_KEY
3. Optional: Configure Langfuse for request logging (LANGFUSE_SECRET_KEY, LANGFUSE_PUBLIC_KEY, LANGFUSE_HOST)

## Key Implementation Details

- Tool calls are enforced as single calls for OpenAI compatibility
- Streaming responses are properly normalized between providers
- The proxy supports both sync and async completion methods
- Error handling preserves original exception information
- Model remapping is configurable via environment variables without code changes
