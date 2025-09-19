# Docker Deployment Guide for Claude Code GPT-5 Proxy

This guide explains how to deploy the Claude Code GPT-5 proxy using Docker and GitHub Container Registry (GHCR).

## 🐳 Docker Image

The Docker image is available in GitHub Container Registry:

```
ghcr.io/teremterem/claude-code-gpt-5:latest
```

## 🚀 Quick Start

### Set up environment variables

First of all, you need to create an `.env` file, **REGARDLESS of which method you use to deploy the container.**

Copy `.env.template` to `.env` to use it as a starting point:
```bash
cp .env.template .env
```

Then, edit `.env` and add your API key(s):
```dotenv
OPENAI_API_KEY=your-openai-api-key-here
# Optional: only needed if you plan to use Anthropic models
# ANTHROPIC_API_KEY=your-anthropic-api-key-here

# More settings (see .env.template for details)
...
```

### Method 1: Using the deployment script

**Run the deployment script:**
```bash
./deploy-docker.sh
```

### Method 2: Using Docker Compose

1. **Start the service:**
   ```bash
   docker-compose up -d
   ```

2. **Check the logs:**
   ```bash
   docker-compose logs -f
   ```

### Method 3: Direct Docker run

```bash
docker run -d \
  --name claude-code-gpt-5 \
  -p 4000:4000 \
  --env-file .env \
  --restart unless-stopped \
  ghcr.io/teremterem/claude-code-gpt-5:latest
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

## 🏥 Health Check

The container includes a health check endpoint:

```bash
curl http://localhost:4000/health
```

## 📊 Monitoring

### View container logs:
```bash
docker logs -f claude-code-gpt-5
```

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

## 🔧 Troubleshooting

### Container won't start
1. Check if port 4000 is available: `lsof -i :4000`
2. Verify environment variables are set correctly
3. Check container logs: `docker logs claude-code-gpt-5`

### Authentication issues
1. Verify your API keys are valid and have sufficient credits
2. Check if OpenAI requires identity verification for GPT-5 access (see [README.md](README.md), section "First time using GPT-5 via API?")

### Performance issues
1. Ensure sufficient memory is available (recommended: 2GB+)
2. Check network connectivity to OpenAI and Anthropic APIs

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

### Docker Compose build

Overlay with the dev version of the compose file when building and running:
```bash
docker-compose -f docker-compose.dev.yml up -d --build
```

This will also map the current directory to the container.

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
