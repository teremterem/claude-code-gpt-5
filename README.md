![Claude Code with GPT-5](claude-code-gpt-5.jpeg)

This repository lets you use **Anthropic's Claude Code** with **OpenAI's GPT-5** as the "smart" model via a local LiteLLM proxy.

## Quick Start ⚡

### Prerequisites

- [OpenAI API key](https://platform.openai.com/settings/organization/api-keys) 🔑
- [Anthropic API key](https://console.anthropic.com/settings/keys) 🔑 *(optional with model remapping)*

**About the Anthropic API key**

Claude Code uses two models: a fast model (for quick actions) and a slow "smart" model. With the new **model remapping feature** (v0.3.0+), you can configure the proxy to automatically redirect all Claude model requests to GPT-5 models, making the Anthropic API key optional. Without remapping, the Anthropic API key is still required for the fast model.

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

   # OPTIONAL: Set if you want to use original Anthropic models
   #ANTHROPIC_API_KEY=your-anthropic-api-key-here

   # RECOMMENDED: Model remapping (makes Anthropic API key optional)
   REMAP_CLAUDE_HAIKU_TO=gpt-5-nano-reason-minimal
   REMAP_CLAUDE_SONNET_TO=gpt-5-reason-medium
   REMAP_CLAUDE_OPUS_TO=gpt-5-reason-high
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

2. **Connect to your proxy**:
   ```bash
   ANTHROPIC_BASE_URL=http://localhost:4000 claude
   ```

   **Using model remapping (recommended)**: If you configured the model remaps in your `.env`, you can use Claude Code normally and all Claude models will automatically be redirected to your chosen GPT-5 models:
   ```bash
   ANTHROPIC_BASE_URL=http://localhost:4000 claude --model claude-3-5-sonnet-20241022
   # This will actually use gpt-5-reason-medium (based on your remap configuration)
   ```

   **Direct GPT-5 model selection**: You can also directly specify GPT-5 models:
   ```bash
   ANTHROPIC_BASE_URL=http://localhost:4000 claude --model gpt-5-reason-medium
   ```

   **Available models for direct use:**
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

3. **That's it!** Your Claude Code client will now use **GPT-5 models** with your chosen reasoning effort level. 🎯

## What's New in v0.3.0 🆕

- **Model Remapping**: Automatically redirect Claude model requests to GPT-5 models via environment variables
- **Optional Anthropic API Key**: No longer required when using model remapping
- **Improved Error Handling**: Better proxy error messages and request adaptation
- **Enhanced Configuration**: More flexible `.env` template with better documentation

## KNOWN PROBLEM

**The `Web Search` tool currently does not work with this setup.** You may see an error like:

```text
API Error (500 {"error":{"message":"Error calling litellm.acompletion for non-Anthropic model: litellm.BadRequestError: OpenAIException - Invalid schema for function 'web_search': 'web_search_20250305' is not valid under any of the given schemas.","type":"None","param":"None","code":"500"}}) · Retrying in 1 seconds… (attempt 1/10)
```

**WORKAROUND:** If your request requires searching the web, temporarily switch back to one of the Claude 4 models using the `/model` command in Claude Code. Claude models remain available alongside `gpt-5` and will use the Anthropic API key from your `.env`.

**The `Fetch` tool DOES work, though (getting web content from specific URLs).**

## P. S. You are welcome to join our [MiniAgents Discord Server 👥](https://discord.gg/ptSvVnbwKt)
