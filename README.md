![Claude Code with GPT-5](claude-code-gpt-5.jpeg)

This repository lets you use **Anthropic's Claude Code CLI** with **OpenAI's GPT-5** via a local LiteLLM proxy.

## Quick Start ⚡

### Prerequisites

- [OpenAI API key](https://platform.openai.com/settings/organization/api-keys) 🔑
- [Anthropic API key](https://console.anthropic.com/settings/keys) - optional 🔑

**About the Anthropic API key**

By default, the provided `.env` template (`.env.template` that you will have to copy to `.env`) remaps Claude models (haiku/sonnet/opus) to GPT‑5 equivalents, so all requests go to OpenAI. If you want to keep using Anthropic for any calls, set `ANTHROPIC_API_KEY` and adjust the `REMAP_*` variables in `.env` (or set some/all of them to empty strings).

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
   Edit `.env` and add your API keys:
   ```dotenv
   OPENAI_API_KEY=your-openai-api-key-here
   # Optional: only needed if you plan to use Anthropic models
   # ANTHROPIC_API_KEY=your-anthropic-api-key-here

   # Recommended: remap Claude models to GPT‑5 variants to ensure all
   # built-in agents in Claude Code also use GPT‑5
   REMAP_CLAUDE_HAIKU_TO=gpt-5-nano-reason-minimal
   REMAP_CLAUDE_SONNET_TO=gpt-5-reason-medium
   REMAP_CLAUDE_OPUS_TO=gpt-5-reason-high

   # Some more optional settings (see .env.template for details)
   ...
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
   ANTHROPIC_BASE_URL=http://localhost:4000 claude
   ```

   **Alternatively, you can override the default model on the side of the CLI using the `--model` parameter:**
   ```bash
   ANTHROPIC_BASE_URL=http://localhost:4000 claude --model gpt-5-reason-low
   ```

3. **That's it!** Your Claude Code client will now use the selected **GPT-5 variant** with your chosen reasoning effort level. 🎯

### Available GPT-5 model aliases

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

> **NOTE:** Apart from the aliases above, you can also use arbitrary model names from OpenAI or Anthropic.

## KNOWN PROBLEM

**The `Web Search` tool currently does not work with this setup.** You may see an error like:

```text
API Error (500 {"error":{"message":"Error calling litellm.acompletion for non-Anthropic model: litellm.BadRequestError: OpenAIException - Invalid schema for function 'web_search': 'web_search_20250305' is not valid under any of the given schemas.","type":"None","param":"None","code":"500"}}) · Retrying in 1 seconds… (attempt 1/10)
```

This is planned to be fixed soon.

> **NOTE:** The `Fetch` tool (getting web content from specific URLs) is not affected and works normally.

## P. S. You are welcome to join our [MiniAgents Discord Server 👥](https://discord.gg/ptSvVnbwKt)
