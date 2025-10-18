<h1 align="center">My LiteLLM Server</h1>

<p align="center">
    <img alt="LibreChat with LiteLLM Server Boilerplate"
        src="https://raw.githubusercontent.com/teremterem/claude-code-gpt-5/main/images/librechat-master-yoda.jpg">
</p>

**A lightweight LiteLLM server boilerplate** pre-configured with `uv` and `Docker` for hosting your own **OpenAI- and Anthropic-compatible endpoints.** Perfect for **LibreChat** (a quick setup of which is included in this repository) or other UI clients. Contains an example of a custom provider that stylizes responses **(Yoda example)** to serve as a starting point for your own custom providers.

> **NOTE:** If you need to go back to the `Claude Code CLI Proxy` version of this repository, click [here](https://github.com/teremterem/claude-code-gpt-5).

## Quick Start ⚡

### Prerequisites

- [OpenAI API key 🔑](https://platform.openai.com/settings/organization/api-keys) (or any other provider's API key that you're planning to use under the hood)
- Either [Docker Desktop](https://docs.docker.com/desktop/) or [uv](https://docs.astral.sh/uv/getting-started/installation/)

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

3. **(Optional) Set up `origin` remote and push your `main` branch to your remote repository:**

   ```bash
   git remote add origin <your-remote-repository-url>
   ```

   ```bash
   git push -u origin main
   ```

   Even though this step is optional, it is generally a good idea to have your own remote repository to push your changes to.

4. **Configure Environment Variables:**

   Copy the template file to create your `.env`:
   ```bash
   cp .env.template .env
   ```

   Edit `.env` and add your OpenAI API key:
   ```dotenv
   OPENAI_API_KEY=your-openai-api-key-here

   # Optional (see .env.template for details):
   # LITELLM_MASTER_KEY=strong-key-that-you-generated

   # Some more optional settings (see .env.template for details)
   ...
   ```

5. **Run your LiteLLM Server with LibreChat and the Yoda example** (make sure to install [Docker Desktop](https://docs.docker.com/desktop/) first):

   ```bash
   ./librechat/run-docker-compose.sh
   ```

   **OR**

   ```bash
   cd librechat
   ```

   Then

   ```bash
   docker compose -p litellm-librechat up
   ```

   Which is equivalent to running:
   ```bash
   docker compose \
      -p litellm-librechat \
      -f docker-compose.yml \
      -f docker-compose.override.yml \
      up
   ```
   > **NOTE:** The last two variants of the direct `docker compose` command require you to be in the `librechat/` subdirectory, hence the `cd` command.

   **That's it.** You should be able to access the LibreChat UI at **http://localhost:3080**, and after registering an account in your local LibreChat instance, you should be able to see something similar to what you see on the screenshot at the beginning of this README.

### Running your LiteLLM Server WITHOUT LibreChat

If you don't want to use LibreChat, you can run your LiteLLM Server directly.

> **NOTE:** This time you are expected to be in the `root directory` of the repository, **not** in the `librechat/` subdirectory.

- **OPTION 1:** Use a script for `uv` (make sure to install [uv](https://docs.astral.sh/uv/getting-started/installation/) first):
   ```bash
   ./uv-run.sh
   ```

- **OPTION 2:** Run via a direct `uv` command:
   ```bash
   uv run litellm --config config.yaml
   ```

- **OPTION 3:** Run via `Docker Compose` (make sure to install [Docker Desktop](https://docs.docker.com/desktop/) first):
   ```bash
   docker-compose \
      -f docker-compose.yml \
      -f docker-compose.dev.yml \
      up
   ```

### Staying up to date with the Boilerplate

Once you start customizing your copy, you will occasionally want to bring in the newest boilerplate improvements. The steps below assume you cloned the boilerplate with the `boilerplate` remote (see the setup section above) and that your own repository is attached as `origin`.

1. **Make sure your working tree is clean.**
   ```bash
   git status
   ```
   Commit or stash anything pending before you proceed.

2. **Fetch the latest boilerplate branch.**
   ```bash
   git fetch boilerplate main-boilerplate
   ```

3. **Switch to your local `main` branch.**
   ```bash
   git switch main
   ```

4. **Merge the upstream updates into your branch.**
   ```bash
   git merge boilerplate/main-boilerplate
   ```
   If Git reports conflicts, resolve the files Git marks, `git add` them, and run `git commit` to complete the merge before continuing.

5. **Push the refreshed branch to your own repository.**
   ```bash
   git push origin main
   ```

That’s it - your `main` branch now contains the latest boilerplate changes while keeping your customizations in place.

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
