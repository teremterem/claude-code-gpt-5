# Repository Guidelines

## Project Structure & Modules
- Root config: `config.yaml` (model routing), `.env` (API keys), `pyproject.toml` (deps/tools).
- Proxy code: `proxy/` package (`custom_llm_router.py`, `route_model.py`, `convert_stream.py`).
- Docs & assets: `README.md`, `claude-code-gpt-5.jpeg`.
- Dev tooling: `.pre-commit-config.yaml`, `.pylintrc`.

## Build, Test, and Dev Commands
- Install deps: `uv sync` (add `--extra langfuse` to enable Langfuse hooks).
- Run proxy: `uv run litellm --config config.yaml` (reads `.env`).
- Format: `uv run black .` (line length 119).
- Lint: `uv run pylint proxy`.
- Pre-commit: `uv run pre-commit install` then `uv run pre-commit run -a`.
- Manual test with Claude Code: `ANTHROPIC_BASE_URL=http://localhost:4000 claude --model gpt-5-reason-medium`.

## Coding Style & Naming
- Python 3.8+; 4-space indent; keep lines ≤119 chars (Black config).
- Use Black for formatting; ensure pylint passes (config in repo).
- Naming: modules/files `snake_case.py`; functions/vars `snake_case`; classes `PascalCase`.
- Keep proxy logic small and focused; place routing in `route_model.py`, provider glue in `custom_llm_router.py`.

## Testing Guidelines
- No automated tests yet. Validate locally by:
  - Starting the proxy and issuing a sample completion with a `gpt-5-*-reason-*` alias.
  - Verifying model alias logs and tool streaming behavior.
- If adding tests, prefer `pytest` under a `tests/` directory; name files `test_*.py`.

## Commit & Pull Requests
- Commits: imperative, concise, present tense; group related changes.
  - Examples: `fix linting errors`, `Integrate Langfuse (#13)`, `split custom_llm_router.py into 3 files`.
- PRs: include purpose, screenshots/logs when relevant, and link issues.
  - Ensure: formatting, lint, and pre-commit pass; update `README.md`/`config.yaml` if behavior changes.

## Security & Configuration
- Store keys only in `.env` (see `.env.template`). Required: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`.
- Known limitation: Claude Code “Web Search” tool is incompatible here; use Claude models for that case.
- Optional telemetry: set `LANGFUSE_*` and install extras to enable logging.
