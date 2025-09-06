# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Repository purpose
- Local LiteLLM proxy so Claude Code can use OpenAI GPT-5 as the smart model while keeping Anthropic models available for fast tasks.

Key commands
- Start proxy: uv run litellm --config config.yaml
- Install deps (exact env from pyproject/uv.lock): uv sync
- Format: uv run black .
- Lint: uv run pylint proxy
- Run pre-commit locally on staged files: uv run pre-commit run -a

Model usage from Claude Code
- Point Claude Code to this proxy when you want GPT-5 variants as the smart model:
  ANTHROPIC_BASE_URL=http://localhost:4000 claude --model gpt-5-reason-medium
- Switch back to Claude models as needed (no proxy base URL required) by choosing a claude-* model.
- Known limitation: Web Search tool is not supported through this proxy; use Claude 4 models if web search is required. Fetch tool works.

High-level architecture
- LiteLLM custom provider bridge configured in config.yaml:
  - model_name: "*" -> custom_provider_map routes all requests to custom_llm_router.CustomLLMRouter
- proxy/custom_llm_router.py: Implements a CustomLLM with completion/astreaming paths that:
  - Resolve requested alias to provider model and parameters via route_model()
  - Call litellm.completion/acompletion (and streaming variants), converting exceptions with raise ... from ...
  - For streaming, converts provider chunks to GenericStreamingChunk via convert_stream.to_generic_streaming_chunk
- proxy/route_model.py: Maps aliases
  - claude-* -> anthropic/claude-*
  - gpt-5(-mini|-nano)?-reason-(minimal|low|medium|high) -> openai/gpt-5[variant] with reasoning_effort set accordingly
  - Prints a concise mapping line for visibility; raises ValueError for unknown aliases
- proxy/convert_stream.py: Best-effort normalization of streaming chunks across providers into GenericStreamingChunk, handling OpenAI delta.tool_calls, Anthropic tool_use, legacy function_call, with conservative fallbacks

Environment and telemetry
- Optional Langfuse: set LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY; router auto-enables litellm success/failure callbacks if installed. Install extras with:
  uv sync --extra langfuse

Development workflow
- Python version: .python-version controls local version; uv.lock pins env
- Run black and pylint before committing (pre-commit hooks are configured). Typical loop:
  uv sync
  uv run black .
  uv run pylint proxy
  uv run pre-commit run -a

Notes for future Claude Code sessions
- No tests currently present. If you add tests, document how to run a single test here.
- To add models, extend config.yaml model_list or enhance route_model mapping.
