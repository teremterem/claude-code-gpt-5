# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Commands
- Start local proxy
  - uv run litellm --config config.yaml
- Lint/format
  - uv run black .
  - uv run pylint proxy
- Typecheck
  - Not configured in this repo
- Tests
  - None present; single-test invocation not applicable
- Use with Claude Code CLI
  - ANTHROPIC_BASE_URL=http://localhost:4000 claude --model gpt-5-reason-medium
  - Models follow: gpt-5(-mini|-nano)-reason-{minimal,low,medium,high}

Architecture
- Goal: Run a local LiteLLM proxy so Claude Code’s “smart” model is served by GPT‑5 variants while the “fast” model remains Anthropic.
- Configuration: config.yaml maps model names to a custom LiteLLM provider implemented in proxy/custom_llm_router.py via custom_provider_map.
- Core modules (proxy/)
  - custom_llm_router.py: LiteLLM custom provider; inspects requested model and routes to the appropriate GPT‑5 family variant, handling streaming.
  - route_model.py: Normalizes model names and reasoning-effort levels to provider-specific IDs/params.
  - convert_stream.py: Adapts provider streaming events into the format expected by clients through LiteLLM.
  - config.py: Loads environment variables and runtime settings.
- Flow: Claude Code CLI → local proxy (LiteLLM) → custom router → OpenAI for GPT‑5 (slow path) or Anthropic passthrough for fast path → stream conversion → client.

Repo Conventions
- Package/runtime: Python with uv; dependencies pinned via uv.lock.
- Formatting: black with line-length 119 (see pyproject.toml [tool.black]).
- Environment: Requires OPENAI_API_KEY and ANTHROPIC_API_KEY available to the proxy.

Notes
- Default proxy URL is http://localhost:4000 (as used by ANTHROPIC_BASE_URL in README).
- If needed, create a .env (README references copying from .env.template) and export keys before starting the proxy.
- To adjust routing behavior, modify config.yaml and proxy/* (especially custom_llm_router.py and route_model.py).
