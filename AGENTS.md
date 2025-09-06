# Repository Guidelines

## Project Structure & Modules
- `proxy/`: core logic
  - `custom_llm_router.py`: LiteLLM custom provider entrypoint
  - `route_model.py`: maps aliases (e.g., `gpt-5-*-reason-*`) to provider models and params
  - `convert_stream.py`: normalizes streaming chunks to `GenericStreamingChunk`
- `config.yaml`: registers `custom_llm_router/*` with LiteLLM proxy
- `.env.template` / `.env`: API keys and optional Langfuse config
- `pyproject.toml`: deps (`litellm[proxy]`), dev tools; `README.md`: usage

## Build, Run, and Dev
- Install deps: `uv sync` (Langfuse: `uv sync --extra langfuse`)
- Start proxy: `uv run litellm --config config.yaml`
- Environment: `cp .env.template .env` and set `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`
- Lint: `uv run pylint proxy`
- Format: `uv run black .`
- Pre-commit: `pre-commit install` then `pre-commit run -a`

## Coding Style & Naming
- Formatter: Black (line length 119); 4-space indentation
- Lint: Pylint (targets Python 3.10 config); fix warnings or justify disables
- Naming: `snake_case` for functions/vars/modules, `PascalCase` for classes, `UPPER_CASE` for constants
- Type hints encouraged; keep functions small and clear

## Testing Guidelines
- No formal test suite yet. For changes in `route_model`, add quick checks, e.g.:
  `uv run python -c "from proxy.route_model import route_model; print(route_model('gpt-5-reason-medium'))"`
- If adding tests, place under `tests/` as `test_*.py` (pytest recommended); document how to run
- In PRs, include repro steps and expected/actual outputs for proxy routing/streaming

## Commit & Pull Requests
- Commits: imperative, concise, scoped. Example: `feat(route_model): add nano variants`
- PRs must include: what/why, linked issues, manual test steps, screenshots/logs (proxy output), and confirm `pre-commit` passes
- Keep diffs focused; update `README.md` or comments when behavior/flags change

## Security & Config Tips
- Never commit secrets; use `.env` (from `.env.template`)
- Keep `GPT_ENFORCE_ONE_TOOL_CALL_PER_RESPONSE=true` to avoid multi-tool-call issues in Claude Code
- Optional: enable Langfuse via env vars; install extras as noted above

## Architecture Overview
- LiteLLM proxy loads `custom_llm_router/*` (see `config.yaml`)
- `CustomLLMRouter` adds provider params (e.g., `reasoning_effort`) and forwards to LiteLLM
- Streaming is normalized in `convert_stream.py` for Claude Code compatibility
- Known limitation: Anthropic Web Search tool unsupported here; see README for workaround
