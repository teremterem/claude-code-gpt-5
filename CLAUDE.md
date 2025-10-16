# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common development commands

Package manager: uv (Python). If you prefer containers, see the Docker section.

- Environment setup
  - Copy and edit env vars:
    ```bash
    cp .env.template .env
    # set OPENAI_API_KEY (required), optionally LITELLM_MASTER_KEY and Langfuse vars
    ```
  - Install Python deps locally with uv (recommended for dev):
    ```bash
    uv sync
    ```

- Run the proxy locally
  - Quick script:
    ```bash
    ./uv-run.sh
    ```
  - Direct command:
    ```bash
    uv run litellm --config config.yaml
    ```
    The proxy listens on port 4000 by default (configurable via env).

- Lint and format
  - Check formatting:
    ```bash
    uv run black --check .
    ```
  - Auto-format:
    ```bash
    uv run black .
    ```
  - Lint (adjust paths as needed):
    ```bash
    uv run pylint common yoda_example
    ```
  - Pre-commit hooks:
    ```bash
    uv run pre-commit install
    uv run pre-commit run --all-files
    ```

- Tests
  - No test suite is present in this repository at the moment.

- Docker usage
  - Dev (local image with live volumes):
    ```bash
    docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
    ```
  - Production-style (pull image):
    ```bash
    docker compose up -d
    ```
  - Stop/cleanup:
    ```bash
    docker compose down
    ```

## High-level architecture

This repository provides a LiteLLM-based proxy that exposes OpenAI-compatible endpoints, plus an example of a custom provider. It is optimized for local development via uv and containerized deployment via Docker.

- Entrypoint and config
  - The service runs the LiteLLM CLI with the repo’s configuration:
    - Entrypoint: `litellm` via `uv run`
    - Configuration: `config.yaml` (declares models and provider mappings)
  - Default port: 4000 (can be overridden via environment variables)

- Custom provider example
  - Location: `yoda_example/yoda_speak.py`
  - Defines a custom provider class that wraps upstream OpenAI calls and injects a Yoda-style system prompt.
  - Supports normal and streaming responses.

- Shared utilities
  - `common/config.py`: Loads environment flags (e.g., tracing switches) and optional Langfuse setup when env vars are present.
  - `common/tracing_in_markdown.py`: Writes request/response traces to `.traces/` as Markdown when enabled.
  - `common/utils.py`: Small helpers (e.g., env flag parsing, streaming chunk shaping).

- Optional UI integration
  - `librechat/` includes a ready-to-use LibreChat configuration wired to this proxy (example models, compose files, and an env template).

- Tooling and quality
  - Formatting: Black
  - Linting: Pylint (config in `.pylintrc`)
  - Git hooks: pre-commit (configured in `.pre-commit-config.yaml`)

## Environment and configuration

- Required
  - `OPENAI_API_KEY`: Upstream API key for the OpenAI-compatible provider used by the proxy

- Recommended
  - `LITELLM_MASTER_KEY`: Enables auth on the proxy if exposing beyond localhost

- Optional
  - `WRITE_TRACES_TO_FILES`: When `true`, saves detailed request/response/stream traces into `.traces/`
  - `LANGFUSE_SECRET_KEY`, `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_HOST`: Enables Langfuse tracing callbacks when present
  - `OPENAI_BASE_URL`: Override upstream base URL if needed
  - `PROXY_PORT`: Override the default 4000 port

- Python and tooling
  - Python version file: `.python-version` (development uses Python 3.13.x)
  - Package/dependency management: uv (`uv sync`, `uv run ...`)

## README highlights for day-to-day use

- Two supported workflows: local (uv) and Docker/Compose
- Quick start: set `.env`, then `./uv-run.sh` or use Docker Compose as outlined above
- Example model demonstrates a custom provider that stylizes responses (Yoda example)
- Container images are published to GHCR for convenience; local images are also supported via the dev Compose overlay

## Notes and gotchas

- Tracing volume: If `WRITE_TRACES_TO_FILES=true`, expect `.traces/` to grow with detailed Markdown logs during usage
- If exposing the proxy externally, set `LITELLM_MASTER_KEY` and ensure network/ingress are configured securely
- Pre-commit hooks run Black and Pylint; install them locally to catch issues before committing

## Extending the proxy

- To add a new custom provider:
  1) Create a module similar to `yoda_example/` (implement the provider class and required methods)
  2) Register it in `config.yaml` under your chosen provider key
  3) Add any env/config toggles in `common/config.py` as needed
  4) Run locally with `uv run litellm --config config.yaml` and verify normal/streaming behavior
