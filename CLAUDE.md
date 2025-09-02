# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository is a LiteLLM proxy configuration that allows Claude Code CLI to use OpenAI's GPT-5 models (and variants) as the "smart" model while retaining Anthropic's fast model for quick operations.

## Common Commands

### Running the Proxy Server
```bash
uv run litellm --config config.yaml
```

### Using Claude Code with GPT-5
```bash
ANTHROPIC_BASE_URL=http://localhost:4000 claude --model gpt-5-reason-low
```

### Environment Setup
```bash
# Copy the environment template
cp .env.template .env

# Edit .env to add your API keys:
# OPENAI_API_KEY=your-openai-api-key
# ANTHROPIC_API_KEY=your-anthropic-api-key
```

### Installing Dependencies
```bash
# Project uses uv for dependency management
uv sync
```

## Architecture

The project consists of:

- **config.yaml**: LiteLLM proxy configuration that maps model names to their providers. Contains GPT-5 variants with different reasoning effort levels (minimal, low, medium, high) for gpt-5, gpt-5-mini, and gpt-5-nano models. Also includes a wildcard mapping for Claude models.

- **pyproject.toml**: Python project configuration using `litellm[proxy]` as the primary dependency.

- **.env**: Required environment variables for both OpenAI and Anthropic API keys. The Anthropic key is still needed because Claude Code uses it for the fast model operations.

## Known Issues

- **Web Search tool does not work** with the GPT-5 setup due to schema validation issues. Workaround: Switch temporarily to Claude models using `/model` command when web search is needed.
- **Web Fetch tool works correctly** for retrieving content from specific URLs.

## Model Configuration

To add new models, modify the `config.yaml` file following this pattern:

```yaml
- model_name: your-custom-model-name
  litellm_params:
    model: provider/model-name
    reasoning_effort: level  # if applicable
```

## Important Notes

- Both OpenAI and Anthropic API keys are required
- First-time GPT-5 API users may need to verify their identity via OpenAI's Persona system
- The proxy runs on localhost:4000 by default
- The project uses Python 3.8+ and manages dependencies with uv