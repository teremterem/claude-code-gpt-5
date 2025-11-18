# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development commands
- **Bootstrap environment variables**: `cp .env.template .env` then fill in `OPENAI_API_KEY` and optional overrides such as `REMAP_CLAUDE_*` (`README.md:35-56`, `.env.template:1-78`).
- **Run the LiteLLM proxy via uv**: `./uv-run.sh` (wraps `uv run litellm --config config.yaml --port 4000 --host 0.0.0.0`) (`README.md:63-71`, `uv-run.sh:5-24`).
- **Direct uv invocation**: `uv run litellm --config config.yaml` if you prefer not to use the helper script (`README.md:68-71`).
- **Docker foreground launch**: `./run-docker.sh` (builds/pulls and runs the container interactively) (`README.md:75-104`, `docs/DOCKER_TIPS.md:31-48`).
- **Docker background launch**: `./deploy-docker.sh` or `docker run -d --name claude-code-gpt-5 -p 4000:4000 --env-file .env ghcr.io/teremterem/claude-code-gpt-5:latest` (`README.md:80-104`, `docs/DOCKER_TIPS.md:31-83`).
- **Docker Compose**: `docker-compose up -d` for the default stack or `docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build` when developing against local sources (`docs/DOCKER_TIPS.md:50-178`).
- **Health and logs**: `docker logs -f claude-code-gpt-5`, `docker ps | grep claude-code-gpt-5`, `curl http://localhost:4000/health` (note API costs on each health probe) (`README.md:96-104`, `docs/DOCKER_TIPS.md:45-145`).
- **Code style / linting** (no automated hook): install dev extras with `uv pip install .[dev]` then run `black .` or `pylint` as needed (`pyproject.toml:15-24`). No test suite is currently defined; add targeted checks per change.

## Architecture overview
- **Runtime flow**: Claude Code CLI points at `http://localhost:4000`, LiteLLM receives the request and dispatches through the custom provider `claude_code_router`, which adapts and forwards to OpenAI GPT-5 (or Anthropic) endpoints (`README.md:108-128`, `config.yaml:1-18`).
- **`claude_code_proxy/` package**
  - `claude_code_router.py` defines the `ClaudeCodeRouter` LiteLLM adapter. It normalizes incoming requests, enforces single-tool responses, switches between Chat Completions and Responses APIs, and writes optional traces (`claude_code_proxy/claude_code_router.py:38-378`).
  - `route_model.py` resolves requested Claude model names into concrete provider/model pairs, handling remaps, reasoning-effort aliases, and logging the mapping (`claude_code_proxy/route_model.py:24-104`).
  - `proxy_config.py` loads environment-driven remap toggles, response-mode settings, and provider constants (`claude_code_proxy/proxy_config.py:7-36`).
- **`common/` utilities** provide shared helpers for environment parsing, tracing, streaming chunk normalization, and tool-call state management (`common/utils.py:1-392`).
- **Configuration and scripts**
  - `config.yaml` registers custom providers and sets the default route for arbitrary model names (`config.yaml:1-18`).
  - Shell helpers (`uv-run.sh`, `run-docker.sh`, `deploy-docker.sh`, `kill-docker.sh`) encapsulate the common launch workflows (`uv-run.sh:1-24`, `docs/DOCKER_TIPS.md:31-135`).
  - Docker artifacts (`Dockerfile`, `docker-compose.yml`, `docker-compose.dev.yml`) support containerized deployment; see `docs/DOCKER_TIPS.md` for usage patterns (`docs/DOCKER_TIPS.md:1-210`).

## Environment configuration
- `.env.template` lists every supported override, including provider remaps, LiteLLM authentication, Responses API toggles, and tracing integrations (`.env.template:1-78`). Copy it to `.env` before running the proxy.
- Default Claude→GPT remaps live in environment variables consumed by `proxy_config.py` and can be disabled by setting them to empty strings (`claude_code_proxy/proxy_config.py:7-20`).
- Optional tracing: enable Langfuse extras or local markdown traces via `WRITE_TRACES_TO_FILES=true` to collect request/response diagnostics (`.env.template:63-76`, `claude_code_proxy/claude_code_router.py:139-216`).

## Working effectively
- When debugging tool-call behavior, inspect the streaming converters in `common/utils.py` and adjust environment flags such as `RESPONSES_TOOL_DEBUG` for verbose output (`common/utils.py:52-171`).
- Remember that Web Search is currently unsupported due to LiteLLM schema constraints; Fetch remains functional (`README.md:150-160`).
