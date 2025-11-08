# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository implements a LiteLLM proxy that allows Claude Code CLI to use OpenAI's GPT-5 models instead of Anthropic's Claude models. It includes custom routing logic, model remapping, and API translation between ChatCompletions and Responses APIs.

## Development Commands

### Running the Proxy

**Using uv (recommended for development):**
```bash
uv run litellm --config config.yaml
```
Or use the convenience script:
```bash
./uv-run.sh
```

**Using Docker:**
```bash
./run-docker.sh              # Foreground
./deploy-docker.sh           # Background
./kill-docker.sh             # Stop and remove container
```

### Code Quality

```bash
# Format code
uv run black .

# Run linting
uv run pylint claude_code_proxy/ common/ yoda_example/

# Install pre-commit hooks
uv run pre-commit install

# Run pre-commit checks manually
uv run pre-commit run --all-files
```

### Testing the Proxy

```bash
# Test with Claude Code CLI (after starting the proxy)
ANTHROPIC_BASE_URL=http://localhost:4000 claude

# If LITELLM_MASTER_KEY is set in .env:
ANTHROPIC_API_KEY="<LITELLM_MASTER_KEY>" \
ANTHROPIC_BASE_URL=http://localhost:4000 \
claude
```

### Installing Dependencies

```bash
# Basic dependencies
uv sync

# With all extras (including Langfuse for tracing)
uv sync --all-extras

# With specific extras
uv sync --extra langfuse
uv sync --extra dev
```

## Architecture

### Core Components

1. **Custom LiteLLM Router** (`claude_code_proxy/claude_code_router.py`)
   - Implements `CustomLLM` interface with 4 methods: `completion`, `acompletion`, `streaming`, `astreaming`
   - Routes all requests through `RoutedRequest` which handles model remapping and API translation
   - Performs prompt injection to enforce single tool calls per response for non-Anthropic models
   - Handles connectivity test requests from Claude Code CLI by adjusting max_tokens and message format

2. **Model Routing** (`claude_code_proxy/route_model.py`)
   - `ModelRoute` class resolves requested models to target models with provider prefixes
   - Handles model remapping (claude-haiku → gpt-5-mini, claude-sonnet → gpt-5, etc.)
   - Extracts reasoning effort from model aliases (e.g., `gpt-5-reason-medium` → `reasoning_effort: medium`)
   - Auto-corrects `gpt5` to `gpt-5`
   - Determines whether to use Responses API (required for GPT-5-Codex)

3. **API Translation** (`common/utils.py`)
   - **ChatCompletions ↔ Responses API conversion:**
     - `convert_chat_messages_to_respapi()`: Converts messages, normalizes roles (tool → user), handles content types
     - `convert_chat_params_to_respapi()`: Converts tools/functions, drops unsupported params
     - `convert_respapi_to_model_response()`: Converts Responses API responses back to ModelResponse
     - `to_generic_streaming_chunk()`: Normalizes streaming chunks from both APIs
   - **Content type normalization:**
     - Maps OpenAI-style types (text, image_url, audio) to Responses API types (input_text, input_image, etc.)
     - Role-based type inference (assistant → output_text, user → input_text, tool → tool_result)
   - **ProxyError:** Custom exception that highlights errors in red (configurable via `PROXY_ERROR_HIGHLIGHT` env var)

4. **Configuration** (`claude_code_proxy/proxy_config.py`, `common/config.py`)
   - Model remapping defaults and environment variable loading
   - `ENFORCE_ONE_TOOL_CALL_PER_RESPONSE`: Inject prompt to limit tool calls (default: true)
   - `ALWAYS_USE_RESPONSES_API`: Force Responses API for all models (default: false)
   - Langfuse integration setup
   - Local tracing to `.traces/` directory (when `WRITE_TRACES_TO_FILES=true`)

5. **LiteLLM Configuration** (`config.yaml`)
   - Registers `claude_code_router` custom handler via `custom_provider_map`
   - Wildcard model mapping: `"*"` → `"claude_code_router/*"` catches all requests
   - Also includes a `yoda_speak` example handler for reference

### Key Design Patterns

- **Prompt Injection for Non-Anthropic Models:** When tools are present, injects a system message instructing the model to call only one tool at a time (Claude Code CLI doesn't support multiple tool calls)

- **Connectivity Test Detection:** Special handling for Claude Code's connectivity tests (`max_tokens=1`, content="quota"|"test") to prevent failures with non-Anthropic models

- **Dual API Support:** Seamlessly switches between ChatCompletions and Responses APIs based on model requirements (GPT-5-Codex requires Responses API)

- **Content Type Aliasing:** Robust handling of various content type naming conventions across different APIs (text/input_text/output_text, image/image_url/input_image, etc.)

- **Tracing:** Optional trace logging to both Langfuse and local markdown files for debugging API interactions

### File Organization

```
claude_code_proxy/          # Main proxy implementation
├── claude_code_router.py   # CustomLLM router with completion/streaming methods
├── route_model.py          # Model name resolution and remapping
└── proxy_config.py         # Configuration loading

common/                     # Shared utilities
├── config.py               # Environment setup, Langfuse integration
├── utils.py                # API conversion utilities, ProxyError
└── tracing_in_markdown.py  # Local trace file writing

yoda_example/               # Example custom LLM handler
config.yaml                 # LiteLLM proxy configuration
pyproject.toml              # Project dependencies and metadata
```

## Important Notes

- **Model Remapping:** By default, claude-haiku → gpt-5-mini-reason-minimal, claude-sonnet → gpt-5-reason-medium, claude-opus → gpt-5-reason-high. Set env vars to empty strings to disable remapping.

- **Reasoning Effort Aliases:** Use `-reason-{minimal|low|medium|high}` or `-reasoning-effort-{level}` suffixes in model names to set reasoning effort (e.g., `gpt-5-reason-high`).

- **Known Issue:** Web Search tool doesn't work due to schema incompatibilities. Fetch tool works normally.

- **Custom Handlers:** To add new custom handlers, register them in `custom_provider_map` in `config.yaml` and implement the `CustomLLM` interface.

- **Pre-commit Hooks:** The project uses Black for formatting and Pylint for linting. Pre-commit hooks enforce these before commits.

- **Testing Changes:** Always test changes with actual Claude Code CLI to ensure compatibility with its specific request patterns and requirements.
