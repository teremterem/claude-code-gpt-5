![Claude Code with GPT-5](claude-code-gpt-5.jpeg)

This repository lets you use **Anthropic's Claude Code** with **OpenAI's GPT-5** as the "smart" model via a local LiteLLM proxy.

## Quick Start ⚡

### Prerequisites

- [OpenAI API key](https://platform.openai.com/settings/organization/api-keys) 🔑
- [Anthropic API key](https://console.anthropic.com/settings/keys) 🔑

**Why the Anthropic API key is still required**

Claude Code uses two models: a fast model (for quick actions) and a slow “smart” model. This setup only replaces the slow model with GPT‑5 via the proxy; the fast model still runs on Anthropic, hence the need for the Anthropic API key.

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
   ANTHROPIC_API_KEY=your-anthropic-api-key-here
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

## P. S. You are very welcome to join our [MiniAgents Discord Server 👥](https://discord.gg/ptSvVnbwKt)
