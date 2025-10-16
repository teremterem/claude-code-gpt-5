<h1 align="center">My LiteLLM Server</h1>

<p align="center">
    <img alt="LibreChat with LiteLLM Server Boilerplate"
        src="https://raw.githubusercontent.com/teremterem/claude-code-gpt-5/main/images/librechat-master-yoda.jpg">
</p>

TODO Add short description of this boilerplate

> **NOTE:** Click [here](https://github.com/teremterem/claude-code-gpt-5) to go back to the `Claude Code CLI Proxy` version of the repo.

## Quick Start ⚡

### Prerequisites

- [OpenAI API key 🔑](https://platform.openai.com/settings/organization/api-keys)
- Either [uv](https://docs.astral.sh/uv/getting-started/installation/) or [Docker Desktop](https://docs.docker.com/desktop/), depending on your preferred setup method

### First time using GPT-5 via API?

If you are going to use GPT-5 via API for the first time, **OpenAI may require you to verify your identity via Persona.** You may encounter an OpenAI error asking you to “verify your organization.” To resolve this, you can go through the verification process here:
- [OpenAI developer platform - Organization settings](https://platform.openai.com/settings/organization/general)

### Setup 🛠️

1. **Clone this repository's `main-boilerplate` branch into a local `main` branch:**
   ```bash
   git clone --branch main-boilerplate --origin boilerplate https://github.com/teremterem/claude-code-gpt-5.git my-litellm-server
   cd my-litellm-server
   git switch -c main
   ```

   TODO Explain the commands above

   TODO Show how to create `origin` remote and push it to your own repository

   TODO Show how to pull the latest changes from the `boilerplate/main-boilerplate` branch and merge them into your local `main` branch which is linked to your own repository (in separate README section)

2. **Configure Environment Variables:**

   Copy the template file to create your `.env`:
   ```bash
   cp .env.template .env
   ```

   Edit `.env` and add your OpenAI API key:
   ```dotenv
   OPENAI_API_KEY=your-openai-api-key-here

   # Optional (see .env.template for details):
   # LITELLM_MASTER_KEY=your-master-key-here

   # Some more optional settings (see .env.template for details)
   ...
   ```

3. **Run the proxy:**

   1) **EITHER via `uv`** (make sure to install [or upgrade to] the **LATEST** version of [uv](https://docs.astral.sh/uv/getting-started/installation/) first):

      **OPTION 1:** Use a script for `uv`:
      ```bash
      ./uv-run.sh
      ```

      **OPTION 2:** Run via a direct `uv` command:
      ```bash
      uv run litellm --config config.yaml
      ```

   2) **OR via `Docker`** (make sure to install [Docker Desktop](https://docs.docker.com/desktop/) first):

      **OPTION 3:** Run `Docker` in the foreground:
      ```bash
      ./run-docker.sh
      ```

      **OPTION 4:** Run `Docker` in the background:
      ```bash
      ./deploy-docker.sh
      ```

      **OPTION 5:** Run `Docker` via a direct command:
      ```bash
      docker run -d \
         --name claude-code-gpt-5 \
         -p 4000:4000 \
         --env-file .env \
         --restart unless-stopped \
         ghcr.io/teremterem/claude-code-gpt-5:latest
      ```
      > **NOTE:** To run with this command in the foreground instead of the background, remove the `-d` flag.

      To see the logs, run:
      ```bash
      docker logs -f claude-code-gpt-5
      ```

      To stop and remove the container, run:
      ```bash
      ./kill-docker.sh
      ```

      > **NOTE:** The `Docker` options above will pull the latest image from `GHCR` and will ignore all your local files except `.env`. For more detailed `Docker` deployment instructions and more options (like building `Docker` image from source yourself, using `Docker Compose`, etc.), see [docs/DOCKER_DEPLOYMENT.md](docs/DOCKER_DEPLOYMENT.md)

## P. S. You are welcome to join our [MiniAgents Discord Server 👥](https://discord.gg/ptSvVnbwKt)

## And if you like the project, please give it a Star 💫

<p align="center">
<a href="https://www.star-history.com/#teremterem/claude-code-gpt-5&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=teremterem/claude-code-gpt-5&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=teremterem/claude-code-gpt-5&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=teremterem/claude-code-gpt-5&type=date&legend=top-left" />
 </picture>
</a>
</p>
