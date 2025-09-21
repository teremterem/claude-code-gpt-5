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

## LiteLLM authentication (LITELLM_MASTER_KEY)

If you route requests through a LiteLLM server that enforces authentication, set LITELLM_MASTER_KEY. This secret is passed through by docker-compose.yml and can be provided via your environment or .env file. If you are not using a LiteLLM router, you can omit it.

If you call Anthropic directly, set ANTHROPIC_API_KEY. When needed, you can also run Claude Code with an inline key:

```bash
ANTHROPIC_API_KEY=sk-ant-... claude
```

If you were previously logged into Claude Code, log out first so the inline key takes effect. When using LiteLLM, provider keys (e.g., ANTHROPIC_API_KEY) are often configured on the router; clients typically only need LITELLM_MASTER_KEY.

Example (.env):

```dotenv
LITELLM_MASTER_KEY=your_litellm_master_key_here
# If calling Anthropic directly (not via LiteLLM):
ANTHROPIC_API_KEY=sk-ant-...
```

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

## 📝 Architecture

```
Claude Code CLI → LiteLLM Proxy (Port 4000) → OpenAI GPT-5 API
```

The proxy handles model routing and ensures compatibility between Claude Code's expectations and OpenAI's GPT-5 responses.
