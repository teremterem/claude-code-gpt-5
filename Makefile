# Makefile for claude-code-gpt-5

.PHONY: help sync sync-dev sync-langfuse sync-all run fmt lint pre-commit-install pre-commit clean test env

PYPROJECT := pyproject.toml
CONFIG := config.yaml

help:
	@echo "Available targets:"
	@echo "  sync                Install base dependencies (uv sync)"
	@echo "  sync-dev            Install dev deps (uv sync --extra dev)"
	@echo "  sync-langfuse       Install Langfuse extra (uv sync --extra langfuse)"
	@echo "  sync-all            Install all extras (uv sync --all-extras)"
	@echo "  run                 Start LiteLLM proxy using config.yaml"
	@echo "  fmt                 Format with Black"
	@echo "  lint                Lint with Pylint"
	@echo "  pre-commit-install  Install pre-commit hooks"
	@echo "  pre-commit          Run all pre-commit hooks"
	@echo "  test                Run pytest (if present)"
	@echo "  env                 Show required env vars"
	@echo "  clean               Remove caches/__pycache__"

sync:
	uv sync

sync-dev:
	uv sync --extra dev

sync-langfuse:
	uv sync --extra langfuse

sync-all:
	uv sync --all-extras

run:
	@test -f .env || (echo "Missing .env; copy from .env.template and set API keys." && exit 1)
	uv run litellm --config $(CONFIG)

fmt:
	uv run black .

lint:
	uv run pylint proxy

pre-commit-install:
	uv run pre-commit install

pre-commit:
	uv run pre-commit run -a

test:
	@command -v pytest >/dev/null 2>&1 || { echo "pytest not installed. Add tests and install via 'uv add -d pytest' or include in dev extras."; exit 0; }
	uv run pytest -q

env:
	@echo "Required: OPENAI_API_KEY, ANTHROPIC_API_KEY"
	@echo "Optional: REMAP_CLAUDE_* (HAIKU/SONNET/OPUS), MODEL_FOR_WEB_SEARCH, OPENAI_ENFORCE_ONE_TOOL_CALL_PER_RESPONSE, LANGFUSE_*"

clean:
	@find . -name "__pycache__" -type d -prune -exec rm -rf {} +
	@find . -name "*.pyc" -delete
