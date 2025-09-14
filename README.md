![Claude Code with GPT-5](claude-code-gpt-5.jpeg)

This repository lets you use **Anthropic's Claude Code** with **OpenAI's GPT-5** as the "smart" model via a local LiteLLM proxy.

## Quick Start ⚡

### Prerequisites

- [OpenAI API key](https://platform.openai.com/settings/organization/api-keys) 🔑
- [Anthropic API key](https://console.anthropic.com/settings/keys) — optional 🔑

By default in v0.3.0, Claude models are remapped to GPT‑5 variants via the proxy. This means an Anthropic API key is not required unless you want to use real Claude models sometimes (see “Claude model remaps” below).

**First time using GPT-5 via API?**

If you are going to use GPT-5 via API for the first time, **OpenAI may require you to verify your identity via Persona.** You may encounter an OpenAI error asking you to “verify your organization.” To resolve this, you can go through the verification process here:
- [OpenAI developer platform - Organization settings](https://platform.openai.com/settings/organization/general)

### Setup 🛠️

1. **Clone this repository**:
   ```bash
   git clone https://github.com/teremterem/claude-code-gpt-5.git
   cd claude-code-gpt-5
   ```

2. **Install [uv](https://docs.astral.sh/uv/)** (if you haven't already):

   **macOS/Linux:**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

   **macOS (using [Homebrew](https://brew.sh/)):**
   ```bash
   brew install uv
   ```

   **Windows (using PowerShell):**
   ```powershell
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

   **Windows (using Scoop):**
   ```bash
   scoop install uv
   ```

   **Alternative: pip install**
   ```bash
   pip install uv
   ```

3. **Configure Environment Variables**:
   Copy the template file to create your `.env`:
   ```bash
   cp .env.template .env
   ```
   Edit `.env` and add your API keys and preferences:
   ```dotenv
   # Required
   OPENAI_API_KEY=your-openai-api-key-here

   # Optional — only needed if you want to use real Claude models sometimes
   # (e.g., when you disable remaps below)
   #ANTHROPIC_API_KEY=your-anthropic-api-key-here

   # Claude model remaps (default: map to GPT‑5 variants)
   # Tip: leave these as-is to make built-in Claude Code agents use GPT‑5 too
   REMAP_CLAUDE_HAIKU_TO=gpt-5-nano-reason-minimal
   REMAP_CLAUDE_SONNET_TO=gpt-5-reason-medium
   REMAP_CLAUDE_OPUS_TO=gpt-5-reason-high

   # Advanced: base URLs (usually not needed to change)
   #OPENAI_BASE_URL=https://api.openai.com/v1
   #ANTHROPIC_BASE_URL=https://api.anthropic.com

   # Recommended: keep the OpenAI single-tool-call guard on
   #OPENAI_ENFORCE_ONE_TOOL_CALL_PER_RESPONSE=true
   ```

4. **Run the server**:
   ```bash
   uv run litellm --config config.yaml
   ```

### Using with Claude Code 🎮

1. **Install Claude Code** (if you haven't already):
   ```bash
   npm install -g @anthropic-ai/claude-code
   ```

2. **Connect to your proxy to use GPT-5 variants**:
   ```bash
   ANTHROPIC_BASE_URL=http://localhost:4000 claude --model gpt-5-reason-medium
   ```

   **Available models for the `--model` parameter:**
   - **GPT-5**:
      - `gpt-5-reason-minimal`
      - `gpt-5-reason-low`
      - `gpt-5-reason-medium`
      - `gpt-5-reason-high`
   - **GPT-5-mini**:
      - `gpt-5-mini-reason-minimal`
      - `gpt-5-mini-reason-low`
      - `gpt-5-mini-reason-medium`
      - `gpt-5-mini-reason-high`
   - **GPT-5-nano**:
      - `gpt-5-nano-reason-minimal`
      - `gpt-5-nano-reason-low`
      - `gpt-5-nano-reason-medium`
      - `gpt-5-nano-reason-high`

3. **That's it!** Your Claude Code client will now use the selected **GPT-5 variant** with your chosen reasoning effort level. 🎯

### Claude model remaps (new in 0.3.0)

- By default, Claude model names used by Claude Code (e.g., haiku/sonnet/opus) are remapped by the proxy to GPT‑5 variants:
  - `claude-*-haiku` → `gpt-5-nano-reason-minimal`
  - `claude-*-sonnet` → `gpt-5-reason-medium`
  - `claude-*-opus` → `gpt-5-reason-high`
- This helps when Claude Code’s built-in agents hardcode Anthropic models, ensuring GPT‑5 is used consistently.
- Customize or disable:
  - Change the `REMAP_CLAUDE_*_TO` variables in `.env` to your preferred models.
  - To use real Claude models, set the remap value(s) to empty strings or comment them out, and provide `ANTHROPIC_API_KEY`.

Note: When calling `claude`, prefer configuring remaps rather than relying only on `--model`, since some built-in agents don’t inherit the global CLI model.

## KNOWN PROBLEM

**The `Web Search` tool currently does not work with this setup.** You may see an error like:

```text
API Error (500 {"error":{"message":"Error calling litellm.acompletion for non-Anthropic model: litellm.BadRequestError: OpenAIException - Invalid schema for function 'web_search': 'web_search_20250305' is not valid under any of the given schemas.","type":"None","param":"None","code":"500"}}) · Retrying in 1 seconds… (attempt 1/10)
```

**WORKAROUND:** If your request requires searching the web, temporarily switch back to one of the Claude 4 models using the `/model` command in Claude Code. Claude models remain available alongside `gpt-5` and will use the Anthropic API key from your `.env`.

**The `Fetch` tool DOES work, though (getting web content from specific URLs).**

## P. S. You are welcome to join our [MiniAgents Discord Server 👥](https://discord.gg/ptSvVnbwKt)
