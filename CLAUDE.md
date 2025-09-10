# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a LiteLLM proxy server that enables using OpenAI's GPT-5 models with Anthropic's Claude Code CLI. The proxy intercepts Claude Code's requests and routes the "smart" model calls to GPT-5 variants while keeping the fast model calls on Anthropic's infrastructure.

## Commands

### Development Setup
```bash
# Install dependencies
uv sync

# Install with optional Langfuse logging support
uv sync --extra langfuse

# Install all optional dependencies including development tools
uv sync --all-extras
```

### Running the Server
```bash
# Start the LiteLLM proxy server with configuration
uv run litellm --config config.yaml
```

### Code Quality
```bash
# Format Python code (line length: 119)
black .

# Run linting (uses .pylintrc configuration)
pylint proxy/

# Run pre-commit hooks
pre-commit run --all-files
```

### Environment Configuration
Copy `.env.template` to `.env` and configure:
- `OPENAI_API_KEY` - Required for GPT-5 access
- `ANTHROPIC_API_KEY` - Required for Claude Code's fast model
- `LANGFUSE_SECRET_KEY`/`LANGFUSE_PUBLIC_KEY` - Optional for request logging

## Architecture

### Core Components

**proxy/custom_llm_router.py** - Main router implementing CustomLLM interface:
- Routes model requests based on patterns
- Handles OpenAI-specific message modifications for tool calling
- Converts between LiteLLM and OpenAI streaming formats

**proxy/route_model.py** - Model routing logic:
- Maps Claude model names to GPT-5 variants based on environment variables
- Supports remapping via `REMAP_CLAUDE_*_TO` environment variables
- Special handling for web search model via `MODEL_FOR_WEB_SEARCH`

**proxy/convert_stream.py** - Stream format conversion:
- Converts OpenAI streaming responses to LiteLLM's GenericStreamingChunk format
- Handles differences between OpenAI and Anthropic streaming APIs

**proxy/config.py** - Configuration management:
- Environment variable loading and validation
- Langfuse integration setup
- Feature flags (e.g., `OPENAI_ENFORCE_ONE_TOOL_CALL_PER_RESPONSE`)

### Request Flow
1. Claude Code sends request to proxy (configured via `ANTHROPIC_BASE_URL`)
2. Custom router identifies if request should use GPT-5 or pass through to Anthropic
3. For GPT-5 requests: messages are modified, routed to OpenAI, response converted back
4. For Claude requests: passed through to Anthropic infrastructure

## Model Mapping

Available GPT-5 model variants for `--model` parameter:
- `gpt-5-reason-minimal/low/medium/high`
- `gpt-5-mini-reason-minimal/low/medium/high`
- `gpt-5-nano-reason-minimal/low/medium/high`

Model remapping via environment variables:
- `REMAP_CLAUDE_HAIKU_TO`
- `REMAP_CLAUDE_SONNET_TO`
- `REMAP_CLAUDE_OPUS_TO`
- `MODEL_FOR_WEB_SEARCH`
