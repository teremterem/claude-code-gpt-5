# Docker Deployment Guide for Claude Code GPT-5

This guide explains how to deploy the Claude Code GPT-5 proxy using Docker and GitHub Container Registry (GHCR).

**Repository**: This is a fork of the original [claude-code-gpt-5](https://github.com/teremterem/claude-code-gpt-5) with added Docker support.

## 🐳 Available Docker Images

The Docker images are available in GitHub Container Registry:

```
ghcr.io/teremterem/claude-code-gpt-5:latest
```

## 🚀 Quick Start

### Method 1: Using the deployment script

1. **Set your environment variables**:
   ```bash
   export OPENAI_API_KEY="your-openai-api-key"
   export ANTHROPIC_API_KEY="your-anthropic-api-key"
   ```

2. **Run the deployment script**:
   ```bash
   ./deploy-docker.sh
   ```

### Method 2: Using Docker Compose

1. **Create a `.env` file**:
   ```bash
   echo "OPENAI_API_KEY=your-openai-api-key" > .env
   echo "ANTHROPIC_API_KEY=your-anthropic-api-key" >> .env
   ```

2. **Start the service**:
   ```bash
   docker-compose up -d
   ```

3. **Check the logs**:
   ```bash
   docker-compose logs -f
   ```

### Method 3: Direct Docker Run

```bash
docker run -d \
  --name claude-code-gpt-5 \
  -p 4000:4000 \
  --env-file .env \
  --restart unless-stopped \
  ghcr.io/teremterem/claude-code-gpt-5:latest
```

*TODO Describe optionally setting up LITELLM_MASTER_KEY ? Will Claude Code be able to work with it ?*

## 📋 Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | ✅ | - | Your OpenAI API key for GPT-5 access |
| `ANTHROPIC_API_KEY` | ✅ | - | Your Anthropic API key for Claude models |
| `OPENAI_ENFORCE_ONE_TOOL_CALL_PER_RESPONSE` | ❌ | `true` | Enforces single tool calls per response |

## 🔧 Usage with Claude Code

Once the proxy is running, use it with Claude Code:

```bash
# Install Claude Code (if not already installed)
npm install -g @anthropic-ai/claude-code

# Use with GPT-5 via the proxy
ANTHROPIC_BASE_URL=http://localhost:4000 claude --model gpt-5-reason-medium
```

### Available GPT-5 Models

- **GPT-5**: `gpt-5-reason-minimal`, `gpt-5-reason-low`, `gpt-5-reason-medium`, `gpt-5-reason-high`
- **GPT-5 Mini**: `gpt-5-mini-reason-minimal`, `gpt-5-mini-reason-low`, `gpt-5-mini-reason-medium`, `gpt-5-mini-reason-high`
- **GPT-5 Nano**: `gpt-5-nano-reason-minimal`, `gpt-5-nano-reason-low`, `gpt-5-nano-reason-medium`, `gpt-5-nano-reason-high`

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
2. Check if OpenAI requires identity verification for GPT-5 access
3. Ensure the Anthropic API key is set (required for fast model operations)

### Performance issues
1. The container is built for `linux/amd64` architecture
2. Ensure sufficient memory is available (recommended: 2GB+)
3. Check network connectivity to OpenAI and Anthropic APIs

## 🏗️ Building from Source

If you need to build the image yourself:

```bash
# TODO TODO TODO
docker build -t claude-code-gpt-5 .

# Build the image
docker build --platform linux/amd64 -t claude-code-gpt-5 .
# TODO TODO TODO What does -t do ?

# TODO TODO TODO Building for both architectures (refer to documentation on how to set up multi-arch building)
echo <YOUR_GITHUB_PAT> | docker login ghcr.io -u <YOUR_GITHUB_USERNAME> --password-stdin

docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t ghcr.io/teremterem/claude-code-gpt-5:<VERSION> \
  -t ghcr.io/teremterem/claude-code-gpt-5:latest \
  --push .

# TODO TODO TODO Then make the package public

# Tag for GHCR (optional)
docker tag claude-code-gpt-5:latest ghcr.io/teremterem/claude-code-gpt-5:latest

# Push to GHCR (optional)
docker push ghcr.io/teremterem/claude-code-gpt-5:latest

# TODO TODO TODO Mention how to do all of the above in one go ?
```

## 🔐 Security Notes

- Keep your API keys secure and never commit them to version control
- Use environment variables or Docker secrets for sensitive data
- Consider running the container in a restricted network environment
- Regularly update the image to get security patches

## 📝 Architecture

```
Claude Code CLI → LiteLLM Proxy (Port 4000) → OpenAI GPT-5 API
                       ↓
               Anthropic API (for fast model)
```

The proxy handles model routing and ensures compatibility between Claude Code's expectations and OpenAI's GPT-5 API format.
