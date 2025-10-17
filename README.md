<h1 align="center">My LiteLLM Server</h1>

<p align="center">
    <img alt="LibreChat with LiteLLM Server Boilerplate"
        src="https://raw.githubusercontent.com/teremterem/claude-code-gpt-5/main/images/librechat-master-yoda.jpg">
</p>

**A lightweight LiteLLM server boilerplate** with prewired `uv` and Docker workflows for hosting your own OpenAI-compatible endpoint. Perfect for **LibreChat** (a quick setup of which is already included in this repository) or other UI clients. Contains an example of a custom provider that stylizes responses **(Yoda example)** to serve as a starting point for your own custom providers.

> **NOTE:** Click [here](https://github.com/teremterem/claude-code-gpt-5) if you need to go back to the `Claude Code CLI Proxy` version of this repository.

## Quick Start ⚡

### Prerequisites

- [OpenAI API key 🔑](https://platform.openai.com/settings/organization/api-keys)
- Either [uv](https://docs.astral.sh/uv/getting-started/installation/) or [Docker Desktop](https://docs.docker.com/desktop/), depending on your preferred setup method

### GPT-5 caveat

If you are going to use GPT-5 via API for the first time, **OpenAI may require you to verify your identity via Persona.** You may encounter an OpenAI error asking you to “verify your organization.” To resolve this, you can go through the verification process here:
- [OpenAI developer platform - Organization settings](https://platform.openai.com/settings/organization/general)

### Setup 🛠️

1. **Clone this repository's `main-boilerplate` branch into a local directory:**
   ```bash
   git clone \
       --branch main-boilerplate \
       --origin boilerplate \
       https://github.com/teremterem/claude-code-gpt-5.git \
       my-litellm-server
   ```

   ```bash
   cd my-litellm-server
   ```

   > **NOTE:** If you want to, you can replace `my-litellm-server` with a different project name in both commands above.

   Notice, that the `git clone` command above uses `boilerplate` as the remote name to link back to the boilerplate repository. **This is because in the next steps you will set up `origin` to link to your own remote repository.**

2. **Create `main` branch from the `main-boilerplate` in your local repository:**

   ```bash
   git switch -c main
   ```

3. **Set up `origin` remote and push your `main` branch to your remote repository:**

   ```bash
   git remote add origin <your-remote-repository-url>
   ```

   ```bash
   git push -u origin main
   ```

   (Even though this step is optional, it is generally a good idea to have your own remote repository to push your changes to.)

4. **Configure Environment Variables:**

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

5. **Run your LiteLLM Server with LibreChat and the Yoda example:**

   ```bash
   ./librechat/run-docker-compose.sh
   ```

   **That's it.** You should be able to access the LibreChat UI at **http://localhost:3080**, and after registering an account in your local LibreChat instance, you should be able to see something similar to what you see on the screenshot at the beginning of this README.

### Running your LiteLLM Server without LibreChat

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

      TODO There isn't really a point in downloading the image from a registry - it's going to be custom anyway

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
         --name my-litellm-server \
         -p 4000:4000 \
         --env-file .env \
         --restart unless-stopped \
         ghcr.io/teremterem/my-litellm-server:latest
      ```
      > **NOTE:** To run with this command in the foreground instead of the background, remove the `-d` flag.

      To see the logs, run:
      ```bash
      docker logs -f my-litellm-server
      ```

      To stop and remove the container, run:
      ```bash
      ./kill-docker.sh
      ```

      > **NOTE:** The `Docker` options above will pull the latest image from `GHCR` and will ignore all your local files except `.env`. For more detailed `Docker` deployment instructions and more options (like building `Docker` image from source yourself, using `Docker Compose`, etc.), see [docs/DOCKER_DEPLOYMENT.md](docs/DOCKER_DEPLOYMENT.md)

TODO Show how to pull the latest changes from the `boilerplate/main-boilerplate` branch and merge them into your local `main` branch which is linked to your own repository (in separate README section)

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
