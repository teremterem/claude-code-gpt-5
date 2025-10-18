# librechat/

This folder contains a self-contained LibreChat stack wired to the LiteLLM server in the repository root. It provides compose definitions, a minimal Dockerfile for baking configuration, and the LibreChat application config that points LibreChat to the local LiteLLM endpoint.

> **NOTE:** This folder does not contain LibreChat source code itself, it only contains the configurations for it (with references to pre-built public Docker images).

For setup, run, and maintenance steps, see the [repository root README.md](../README.md).

If you want to learn more about LibreChat, see the [official LibreChat documentation](https://www.librechat.ai/docs) as well as the [official LibreChat repository](https://github.com/danny-avila/LibreChat) for their maintained examples and documentation.

## What lives here and why

**docker-compose.yml**

- Baseline compose file **(copied from the LibreChat official repo)**. Defines the core LibreChat services: API (`api`), MongoDB (`mongodb`), Meilisearch (`meilisearch`), a Postgres+pgvector instance (`vectordb`), and the RAG API (`rag_api`).
- Binds this folder’s `.env` into the API container and mounts local directories for images, uploads, and logs.

**docker-compose.override.yml**

- Project-specific overlay that integrates the local LiteLLM server into the LibreChat stack as a `litellm` service (builds from the repo root).
- Pins LibreChat API and RAG API images to specific tags for reproducibility.
- Mounts this folder’s `librechat.yaml` into the API container, ensuring the LibreChat UI uses the configuration committed in this repo.
- Sets `LITELLM_BASE_URL=http://litellm:4000/v1` for the API container so LibreChat talks to the `litellm` service over the compose network.
- Includes volumes to speed up local Python dependency management for LiteLLM (`.venv`, uv cache).

**docker-compose.override.yml.example**

- Sample override file kept for reference **(copied from the LibreChat official repo)**. Demonstrates a wide range of optional LibreChat overrides (extra services, alternate images, storage tweaks) that you can copy into a custom override if you need functionality beyond this project’s tailored setup.

**deploy-compose.yml**

- Deployment-style compose file **(copied from the LibreChat official repo)**. Adds a separate `client` NGINX service that fronts the API and publishes ports 80/443 for production-like hosting while still mounting this folder’s `librechat.yaml`. **Not used in current setup - placed here for reference only.**

**Dockerfile**

- Minimal Dockerfile that extends an official LibreChat image and bakes in `librechat.yaml` at build time. Useful when publishing a preconfigured LibreChat image so external deployments do not need to inject the config file at runtime.

**librechat.yaml**

- LibreChat application configuration. In this repo it defines a single custom endpoint named `LiteLLM` and wires it to the LiteLLM server via two environment variables:
  - `LITELLM_MASTER_KEY` – the key LibreChat sends with requests to authenticate to LiteLLM
  - `LITELLM_BASE_URL` – the base URL for the LiteLLM server’s OpenAI-compatible API
- The `modelSpecs` section intentionally restricts the visible model list to a single entry (`yoda`) with a human-friendly label. This keeps the UI focused on the example custom provider shipped in this repository.

**librechat.example.yaml**

- Sample configuration retained as a reference for the full LibreChat feature surface **(copied from the LibreChat official repo)**. Useful when you need to explore advanced settings or restore defaults not covered by this project’s trimmed-down `librechat.yaml`.

**.env and .env.example**

- Environment files consumed by LibreChat services (API, Meilisearch, RAG API). They centralize service ports, search settings, and other application options used by the compose files.

**.env.non-secure-litellm-master-key**

- A convenience file that supplies a non-secure placeholder for `LITELLM_MASTER_KEY` when the root `.env` does not provide one. Its purpose is to prevent compose from failing in local development scenarios where a real key is not set.

**run-docker-compose.sh**

- Stops any existing LibreChat stack for this project and starts it again with the compose files in this folder.

**images/, uploads/, logs/**

- Bind-mounted data directories referenced by the compose files. These hold user-visible assets, uploaded files, and application logs during local runs (excluded from the repo using `.gitignore`).

## How this folder fits the repo

- The override compose file introduces a `litellm` service built from the repository root, connecting the LibreChat UI to the LiteLLM server defined by this project.
- `librechat.yaml` tells LibreChat to route requests to that service using an OpenAI-compatible endpoint, while `modelSpecs` keeps the UI scoped to the example `yoda` model to demonstrate a custom provider.
- The included Dockerfile enables producing a preconfigured LibreChat image that embeds this repository’s `librechat.yaml`, which simplifies external deployments.

For any operational steps (creating environment files, starting the stack, publishing images, etc.), refer to the [main README.md](../README.md) at the repository root.
