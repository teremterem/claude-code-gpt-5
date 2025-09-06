# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

- Default runtime: Python 3.13 (see .python-version). Use uv for env and execution.
- Primary purpose: Run a LiteLLM proxy that routes Claude Code requests to GPT‑5 variants for the “smart” model while leaving Claude models available for fast tasks.

Commands
- Install deps (no venv activation needed with uv):
  - uv sync --all-extras
- Run proxy:
  - uv run litellm --config config.yaml
- Lint & format:
  - uv run black .
  - uv run pylint proxy
- Pre-commit locally:
  - uv run pre-commit run -a

Running Claude Code against this proxy
- Make sure ANTHROPIC_API_KEY and OPENAI_API_KEY are set (see .env.template).
- Launch Claude Code pointing to the proxy base URL and choose a GPT‑5 variant, e.g.:
  - ANTHROPIC_BASE_URL=http://localhost:4000 claude --model gpt-5-reason-medium
- Web Search tool is not supported through this proxy; Fetch works. If you need Web Search, switch temporarily to a Claude 4 model with /model.

Architecture overview
- LiteLLM config (config.yaml):
  - model_list: "*" maps to custom provider custom_llm_router/*.
  - litellm_settings.custom_provider_map: binds provider name custom_llm_router to Python handler proxy.custom_llm_router.custom_llm_router.
- Custom provider (proxy/custom_llm_router.py):
  - Implements a CustomLLM that forwards completion/streaming calls to litellm after routing and augmenting params.
  - If LANGFUSE keys are present, enables litellm success/failure callbacks for Langfuse telemetry.
  - Key entrypoint exported as custom_llm_router.
- Model routing (proxy/route_model.py):
  - Accepts friendly aliases like gpt-5(-mini|-nano)-reason-(minimal|low|medium|high).
  - Maps to provider models openai/gpt-5[(-mini|-nano)] and injects reasoning_effort accordingly.
  - Passes through claude-* to anthropic/claude-* so Claude Code’s fast model continues to work via Anthropic.
- Streaming normalization (proxy/convert_stream.py):
  - Converts provider-specific streaming chunks to LiteLLM’s GenericStreamingChunk shape.
  - Handles OpenAI-style delta/tool_calls, Anthropic tool_use, and legacy function_call best‑effort.

Conventions & notes
- Python style: black line-length 119; run pylint clean (see .pylintrc). Pre-commit enforces black/pylint and basic checks.
- Keep secrets in .env; never commit .env. Use .env.template as reference.
- To add more models, extend config.yaml model_list or enhance route_model.
- No tests are present currently.
