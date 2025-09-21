# Docker Deployment Guide for Claude Code GPT-5 Proxy

This guide explains how to deploy the Claude Code GPT-5 proxy using Docker and GitHub Container Registry (GHCR).

## 🐳 Docker Image

The Docker image is available in GitHub Container Registry:

```
ghcr.io/teremterem/claude-code-gpt-5:latest
```

## 🚀 Quick Start

### Method 1: Using the deployment script

1. **Copy `.env.template` to `.env`:**
   ```bash
   cp .env.template .env
   ```

2. **Edit `.env` and add your OpenAI API key:**
   ```dotenv
   OPENAI_API_KEY=your-openai-api-key-here

   # More settings (see .env.template for details)
   ...
   ```

3. **Run the deployment script:**

   Run in the foreground:
   ```bash
   ./run-docker.sh
   ```

   Alternatively, to run in the background:
   ```bash
   ./deploy-docker.sh
   ```

4. **Check the logs** (if you ran in the background):
   ```bash
   docker logs -f claude-code-gpt-5
   ```

### Method 2: Using Docker Compose

1. **Export your OpenAI API key as an env var**, as well as any other vars from `.env.template` if you would like to modify the defaults (our default Compose setup DOES NOT load env vars from `.env`):
   ```bash
   export OPENAI_API_KEY=your-openai-api-key-here
   ```

2. **Start the service:**
   ```bash
   docker-compose up -d
   ```
   > **NOTE:** To run in the foreground, remove the `-d` flag.

3. **Check the logs:**
   ```bash
   docker-compose logs -f
   ```

### Method 3: Direct Docker run

1. **Copy `.env.template` to `.env`:**
   ```bash
   cp .env.template .env
   ```

2. **Edit `.env` and add your OpenAI API key:**
   ```dotenv
   OPENAI_API_KEY=your-openai-api-key-here

   # More settings (see .env.template for details)
   ...
   ```

3. **Run the container:**
   ```bash
   docker run -d \
   --name claude-code-gpt-5 \
   -p 4000:4000 \
   --env-file .env \
   --restart unless-stopped \
   ghcr.io/teremterem/claude-code-gpt-5:latest
   ```

   > **NOTE:** You can also supply the environment variables individually via the `-e` parameter, instead of `--env-file .env`

   > **NOTE:** To run in the foreground, remove the `-d` flag.

4. **Check the logs:**
   ```bash
   docker logs -f claude-code-gpt-5
   ```

## 🔧 Usage with Claude Code

Once the proxy is running, use it with Claude Code:

1. **Install Claude Code** (if not already installed):
   ```bash
   npm install -g @anthropic-ai/claude-code
   ```

2. **Use with GPT-5 via the proxy:**
   ```bash
   ANTHROPIC_BASE_URL=http://localhost:4000 claude
   ```

> Tip: If Claude Code is currently logged-in to Anthropic, you may need to log out in the CLI so it stops using Anthropic's cloud. You can then run with `ANTHROPIC_BASE_URL` pointing to your local proxy. You can also set `ANTHROPIC_API_KEY` inline before the command to ensure the CLI always includes an API key (some flows require it), e.g. `ANTHROPIC_API_KEY=dummy ANTHROPIC_BASE_URL=http://localhost:4000 claude`.

## 📊 Monitoring

### Check container status:
```bash
docker ps | grep claude-code-gpt-5
```

### Monitor resource usage:
```bash
docker stats claude-code-gpt-5
```

## 🛑 Stopping and Cleanup

### Stop the container:
```bash
docker stop claude-code-gpt-5
```

### Remove the container:
```bash
docker rm claude-code-gpt-5
```

### Using Docker Compose:
```bash
docker-compose down
```

## 🏥 Health Check

The container includes a health check endpoint:

```bash
curl http://localhost:4000/health
```

## 🏗️ Building from Source

If you need to build the image yourself.

### Direct Docker build

1. First build the image:
   ```bash
   docker build -t claude-code-gpt-5 .
   ```

2. Then run the container:
   ```bash
   docker run -d \
     --name claude-code-gpt-5 \
     -p 4000:4000 \
     --env-file .env \
     --restart unless-stopped \
     claude-code-gpt-5
   ```
   > **NOTE:** To run in the foreground, remove the `-d` flag.

### Docker Compose build

Build and run, but overlay with the dev version of Compose setup:
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
```

This will also map the current directory to the container.

> **NOTE:** The dev version of the Compose setup DOES use the `.env` file, so you will need to set up your environment variables in `.env`

> **NOTE:** To run in the foreground, remove the `-d` flag.

## 🔧 Troubleshooting

### Container won't start
1. Check if port 4000 is available: `lsof -i :4000`
2. Verify environment variables are set correctly
3. Check container logs: `docker logs -f claude-code-gpt-5`

### Authentication issues
1. Verify your API keys are valid and have sufficient credits
2. Check if OpenAI requires identity verification for GPT-5 access (see [README.md](README.md), section "First time using GPT-5 via API?")

### Performance issues
1. Ensure sufficient memory is available (recommended: 2GB+)
2. Check network connectivity to OpenAI and Anthropic APIs

## 🔐 Security Notes

- Keep your API keys secure and never commit them to version control
- Use environment variables or Docker secrets for sensitive data
- Consider running the container in a restricted network environment
- Regularly update the image to get security patches

### Optional proxy authentication (master key)

If you set the `LITELLM_MASTER_KEY` environment variable, the proxy will require clients to authenticate on every request.

- Server-side: set `LITELLM_MASTER_KEY` (e.g., in `.env` or your environment)
- Client-side: send either header with the same value
  - `Authorization: Bearer <LITELLM_MASTER_KEY>`
  - `X-API-KEY: <LITELLM_MASTER_KEY>`

Example with Docker Compose (env already passed through by default compose file):

```bash
export LITELLM_MASTER_KEY=super-secret
docker-compose up -d
```

Example direct Docker run:

```bash
docker run -d \
  --name claude-code-gpt-5 \
  -p 4000:4000 \
  -e LITELLM_MASTER_KEY=super-secret \
  --env-file .env \
  --restart unless-stopped \
  ghcr.io/teremterem/claude-code-gpt-5:latest
```

When using Claude Code CLI, add the header via environment variable pass-through:

```bash
ANTHROPIC_BASE_URL=http://localhost:4000 \
ANTHROPIC_API_KEY=dummy \
LITELLM_MASTER_KEY=super-secret \
claude
```

Claude Code reads `ANTHROPIC_API_KEY` for authentication even when talking to a self-hosted proxy. Any non-empty value works if your proxy enforces `LITELLM_MASTER_KEY`; the real access control is performed by the proxy using the header derived from these variables.

## 📝 Architecture

```
Claude Code CLI → LiteLLM Proxy (Port 4000) → OpenAI GPT-5 API
```

The proxy handles model routing and ensures compatibility between Claude Code's expectations and OpenAI's GPT-5 responses.
