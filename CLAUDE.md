# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This project is a **LiteLLM proxy server** that enables Claude Code CLI to work with OpenAI's GPT-5 models by intercepting and routing API requests. The core functionality involves:

1. **Model routing and remapping**: Automatically remaps Claude model names (claude-sonnet, claude-haiku, etc.) to GPT-5 variants with configurable reasoning effort levels
2. **API translation**: Converts between ChatCompletions API and Responses API formats when needed (e.g., for GPT-5-Codex)
3. **Tool call enforcement**: Injects prompts to force non-Anthropic models to call only one tool per response (Claude Code CLI limitation)

## Architecture

### Core Components

**`claude_code_proxy/`** - Main proxy routing logic
- `claude_code_router.py`: Implements `ClaudeCodeRouter` (CustomLLM) with 4 methods: `completion`, `acompletion`, `streaming`, `astreaming`. Each creates a `RoutedRequest` that handles model remapping and API conversions.
- `route_model.py`: `ModelRoute` class handles model name parsing, remapping (Haiku→gpt-5-mini, Sonnet→gpt-5, Opus→gpt-5-high), reasoning effort extraction from aliases (e.g., `gpt-5-reason-medium`), and provider prefix resolution.
- `proxy_config.py`: Loads environment variables for model remapping and feature flags.

**`common/`** - Shared utilities
- `config.py`: Global configuration including Langfuse integration and trace file settings.
- `utils.py`: Contains critical API conversion logic:
  - `convert_chat_messages_to_respapi()`: Converts ChatCompletions messages to Responses API format (handles role mapping, content normalization, tool results)
  - `convert_chat_params_to_respapi()`: Converts request parameters (tools, tool_choice, etc.)
  - `convert_respapi_to_model_response()`: Converts Responses API responses back to ModelResponse
  - `to_generic_streaming_chunk()`: Normalizes streaming chunks from different API formats
- `tracing_in_markdown.py`: Writes detailed request/response traces as markdown files to `.traces/` for debugging.

**`config.yaml`** - LiteLLM configuration that registers `claude_code_router` as a custom provider with wildcard routing (`"*"` → `claude_code_router/*`).

### Key Flow

1. Claude Code CLI sends request to LiteLLM proxy
2. LiteLLM routes to `claude_code_router` via wildcard match
3. `RoutedRequest` object created:
   - Parses model name via `ModelRoute`
   - Applies remapping (e.g., `claude-sonnet-4.5` → `gpt-5-reason-medium`)
   - Injects single-tool-call prompt if needed (see `_adapt_for_non_anthropic_models`)
   - Converts to Responses API if `use_responses_api=True`
4. Calls upstream model via `litellm.completion()` or `litellm.responses()`
5. Converts response back to expected format
6. Returns to Claude Code CLI

### Model Alias System

The proxy supports convenient aliases for GPT-5 models with reasoning effort:
- Pattern: `{model}-reason-{effort}` or `{model}-reasoning-effort-{effort}`
- Examples: `gpt-5-reason-medium`, `gpt-5-mini-reason-minimal`, `gpt-5-nano-reason-high`
- Reasoning efforts: `minimal`, `low`, `medium`, `high`
- The `ModelRoute` class extracts effort from model name and passes as `reasoning_effort` parameter

## Common Commands

### Running the Proxy

**Via uv (local development):**
```bash
uv run litellm --config config.yaml
# Or use the convenience script:
./uv-run.sh
```

**Via Docker:**
```bash
# Foreground:
./run-docker.sh

# Background (with auto-restart):
./deploy-docker.sh

# Stop:
./kill-docker.sh

# View logs:
docker logs -f claude-code-gpt-5
```

### Using with Claude Code CLI

```bash
# Basic usage:
ANTHROPIC_BASE_URL=http://localhost:4000 claude

# With master key authentication:
ANTHROPIC_API_KEY="<LITELLM_MASTER_KEY>" \
ANTHROPIC_BASE_URL=http://localhost:4000 \
claude
```

### Code Quality

**Linting:**
```bash
# Run pylint on all Python files
uv run pylint claude_code_proxy/ common/ yoda_example/

# Run pre-commit hooks manually
uv run pre-commit run --all-files
```

**Formatting:**
```bash
# Format code with Black (line length: 119)
uv run black claude_code_proxy/ common/ yoda_example/
```

## Development Notes

### Environment Variables

Key variables in `.env` (see `.env.template` for full list):
- `OPENAI_API_KEY`: Required for GPT-5 access
- `ANTHROPIC_API_KEY`: Optional, only if you want to keep some Claude models unmapped
- `REMAP_CLAUDE_{HAIKU,SONNET,OPUS}_TO`: Control model remapping (defaults: gpt-5-mini-reason-minimal, gpt-5-reason-medium, gpt-5-reason-high)
- `ENFORCE_ONE_TOOL_CALL_PER_RESPONSE`: Default `true`, injects prompt to limit tool calls (recommended to keep enabled)
- `ALWAYS_USE_RESPONSES_API`: Default `false`, forces Responses API for all models (not recommended)
- `WRITE_TRACES_TO_FILES`: Enable markdown trace files in `.traces/` for debugging
- `LANGFUSE_*`: Optional Langfuse observability integration

### Adding Custom Providers

See `yoda_example/` for a reference implementation of a custom LiteLLM provider. To add your own:

1. Create a new directory with your custom handler (inherit from `CustomLLM`)
2. Implement the 4 required methods: `completion`, `acompletion`, `streaming`, `astreaming`
3. Register in `config.yaml`:
   ```yaml
   litellm_settings:
     custom_provider_map:
     - provider: your_provider_name
       custom_handler: your_module.your_handler

   model_list:
   - model_name: your_model_alias
     litellm_params:
       model: your_provider_name/your_model
   ```

### Debugging with Traces

Enable `WRITE_TRACES_TO_FILES=true` in `.env` to write detailed request/response traces:
- `.traces/YYYYMMDD_HHMMSS_fffff_REQUEST.md` - Original and converted request
- `.traces/YYYYMMDD_HHMMSS_fffff_RESPONSE.md` - Response (for non-streaming)
- `.traces/YYYYMMDD_HHMMSS_fffff_RESPONSE_STREAM.md` - All chunks (for streaming)

Traces show both ChatCompletions API and Responses API representations, making it easy to debug conversion issues.

### Known Limitations

- **Web Search tool**: Currently not working (returns 500 error about invalid schema). Planned fix.
- **Responses API support**: Work in progress, unreliable. GPT-5-Codex requires Responses API but is experimental.
- **Multiple tool calls**: Claude Code CLI doesn't support multiple tool calls per response, hence the single-tool-call enforcement.

### Project Structure Notes

- `librechat/`: Contains LibreChat integration files (separate from main proxy functionality)
- `yoda_example/`: Example custom provider that forces Yoda-speak responses (educational reference)
- `.traces/`: Git-ignored directory for debug traces (created when `WRITE_TRACES_TO_FILES=true`)
- `.venv/`: Python virtual environment (managed by uv)
- `README_BOILERPLATE.md`: Documentation for using this repo as a boilerplate (see main-boilerplate branch)

### Python Version

- Requires Python `>=3.8.1,<4.0, !=3.9.7` (per LiteLLM requirements)
- Currently using Python 3.13 (see `.python-version`)
