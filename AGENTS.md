# Repository Guidelines

## Project Structure & Module Organization
- `proxy/`: Python source for the LiteLLM custom provider.
  - `custom_llm_router.py`: routes requests and handles sync/async/streaming.
  - `route_model.py`: maps friendly aliases (e.g., `gpt-5-*-reason-*`) to provider models.
  - `convert_stream.py`: normalizes streaming chunks to a generic shape.
- `config.yaml`: LiteLLM config; points to the custom provider.
- `.env.template` → copy to `.env` for local secrets.
- `pyproject.toml`: dependencies (`litellm[proxy]`) and dev tooling.
- `README.md`: quick start and usage with Claude Code.

## Build, Test, and Development Commands
- Create env and install deps (recommended):
  - `uv sync --extra dev` (dev tools: black, pylint, pre-commit)
  - `uv sync --extra langfuse` (optional logging integration)
- Run proxy locally:
  - `uv run litellm --config config.yaml`
  - Then point Claude Code: `ANTHROPIC_BASE_URL=http://localhost:4000 claude --model gpt-5-reason-medium`
- Lint & format: `uv run black .` and `uv run pylint proxy`
- Pre-commit: `uv run pre-commit install` then `uv run pre-commit run -a`

## Coding Style & Naming Conventions
- Python 3.8+ (repo uses 3.13 locally); format with Black (line length 119).
- Pylint enabled via `.pylintrc`; keep functions small and errors explicit.
- Modules: snake_case files; functions/vars snake_case; classes PascalCase.
- Prefer explicit errors and small, composable helpers in `proxy/`.

## Testing Guidelines
- No test suite yet. If adding tests, use `pytest` with files named `test_*.py` under `tests/`.
- Aim for coverage on `route_model` mapping and streaming conversions.
- Example: `uv run pytest -q` (after adding `pytest` to dev deps).

## Commit & Pull Request Guidelines
- Commits: present-tense, concise (e.g., "Fix routing for gpt-5-mini").
- PRs: include a summary, reproduction/validation steps, config changes, and screenshots/logs when relevant. Link issues.

## Security & Configuration Tips
- Never commit `.env`; use `.env.template` as reference.
- Required keys: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`. Optional: `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`.
- Edit models in `config.yaml`; keep sensitive values in env vars.
