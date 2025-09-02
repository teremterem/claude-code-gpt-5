# Repository Guidelines

## Project Structure & Module Organization
- Root files: `config.yaml` (LiteLLM proxy models), `README.md` (usage), `.env.template` (sample env), `pyproject.toml` (Python project metadata), `uv.lock`.
- No app source directory yet; this repo primarily configures and runs a local proxy.
- Add code in a new `src/` package and tests in `tests/` if you extend functionality.

## Build, Test, and Development Commands
- Setup env file: `cp .env.template .env` then add API keys.
- Run proxy: `uv run litellm --config config.yaml` (starts on `http://localhost:4000`).
- Use with Claude Code: `ANTHROPIC_BASE_URL=http://localhost:4000 claude --model gpt-5-reason-low`.
- If you add Python modules: run tests with `uv run pytest` (when `tests/` exists).

## Coding Style & Naming Conventions
- Python 3.8+; prefer PEP 8 with 4‑space indentation and `snake_case` for functions/modules.
- Use type hints and docstrings for new public functions.
- No formatter/linter is configured; keep imports sorted and lines ≤ 100 chars.

## Testing Guidelines
- Framework: `pytest` (add to `[project.optional-dependencies]` if you introduce tests).
- Place tests under `tests/` mirroring package layout; name files `test_*.py` and functions `test_*`.
- Aim for meaningful coverage on new/changed code paths; keep tests hermetic (no network).

## Commit & Pull Request Guidelines
- Commits: short, imperative subject (≤ 72 chars), e.g., `add gpt‑5‑mini variants`, `update README`.
- Reference issues when relevant: `fix: map claude-* to anthropic (#12)`.
- PRs: include a clear summary, rationale, test/verification steps (commands to run), and screenshots for docs/UI changes. Update `README.md` and `config.yaml` examples when behavior changes.

## Security & Configuration Tips
- Do not commit secrets. Keep keys only in `.env`; use `.env.template` for placeholders.
- Changes to `config.yaml` affect exposed models; verify startup and a sample request before merging.
- Known limitation: Claude Code “Web Search” tool is unsupported via this proxy; document any workarounds.

## Architecture Notes
- Thin proxy via LiteLLM maps friendly model names (e.g., `gpt-5-reason-low`) to provider models defined in `config.yaml`, enabling Claude Code to call GPT‑5 while preserving Anthropic fast‑model calls.

