# Repository Guidelines

## Project Structure & Module Organization
- `proxy/`: Core Python package (routing, config, stream conversion).
  - `custom_llm_router.py`: LiteLLM custom provider entrypoint.
  - `route_model.py`: Model remapping and provider resolution.
  - `config.py`: Env-based toggles (e.g., remaps, Langfuse, tool-call policy).
  - `convert_stream.py`: Normalizes streaming chunks.
- `config.yaml`: LiteLLM config wiring the custom provider.
- `pyproject.toml`: Dependencies and dev tools.
- `README.md`: User setup and usage.
- `.pre-commit-config.yaml`, `.pylintrc`: Formatting/lint rules.

## Build, Test, and Development Commands
- Install deps: `uv sync` (optional extras: `uv sync --extra langfuse`).
- Run proxy: `uv run litellm --config config.yaml`.
- Format: `uv run black .`
- Lint: `uv run pylint proxy`
- Pre-commit: `uv run pre-commit install && uv run pre-commit run -a`
- Local check (Claude Code): `ANTHROPIC_BASE_URL=http://localhost:4000 claude --model gpt-5-reason-medium`

## Coding Style & Naming Conventions
- Use Black (line length 119) and 4-space indentation.
- Pylint configured in `.pylintrc`; keep functions/variables `snake_case`, classes `PascalCase`, constants `UPPER_CASE`.
- Prefer small, focused modules under `proxy/`. Avoid one-letter names.
- Type hints required for new public functions.

## Testing Guidelines
- No test suite yet. If adding tests, use `pytest` with files named `test_*.py` mirroring `proxy/` structure.
- Cover routing (`route_model`) and message mutation logic.
- For manual verification: run the proxy and exercise model aliases and tool calls via Claude Code.

## Commit & Pull Request Guidelines
- Commit style: short, imperative subjects; keep scope clear (e.g., "fix", "refactor", "bump").
- Reference issues/PRs when relevant (e.g., `(#23)`). Group lockfile bumps separately.
- PRs must include: summary, rationale, testing notes/commands, screenshots only if UX changes, and any config/env impacts.

## Security & Configuration Tips
- Required env: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY` (see `.env.template`).
- Optional: `REMAP_CLAUDE_*`, `MODEL_FOR_WEB_SEARCH`, `OPENAI_ENFORCE_ONE_TOOL_CALL_PER_RESPONSE`.
- Do not commit secrets; rely on `.env` and CI secrets.
