# Docker Deployment Guide for the LiteLLM Server

This guide explains how to deploy the LiteLLM Server using Docker.

## 🐳 Docker Image

The Docker image is available in GitHub Container Registry:

```
ghcr.io/teremterem/my-litellm-server:latest
```

## 🚀 Quick Start

1. **Copy `.env.template` to `.env`:**
   ```bash
   cp .env.template .env
   ```

2. **Edit `.env` and add your OpenAI API key:**
   ```dotenv
   OPENAI_API_KEY=your-openai-api-key-here

   # Optional (see .env.template for details):
   # LITELLM_MASTER_KEY=your-master-key-here

   # More settings (see .env.template for details)
   ...
   ```

### Method 1: Using the deployment script

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
   docker logs -f my-litellm-server
   ```

### Method 2: Using Docker Compose

3. **Start the service:**
   ```bash
   docker-compose up -d
   ```
   > **NOTE:** To run in the foreground, remove the `-d` flag.

4. **Check the logs:**
   ```bash
   docker-compose logs -f
   ```

### Method 3: Direct Docker run

3. **Run the container:**
   ```bash
   docker run -d \
     --name my-litellm-server \
     -p 4000:4000 \
     --env-file .env \
     --restart unless-stopped \
     ghcr.io/teremterem/my-litellm-server:latest
   ```

   > **NOTE:** To run in the foreground, remove the `-d` flag.

   > **NOTE:** You can also supply the environment variables individually via the `-e` parameter, instead of `--env-file .env`

4. **Check the logs:**
   ```bash
   docker logs -f my-litellm-server
   ```

## 📊 Monitoring

### Check container status:
```bash
docker ps | grep my-litellm-server
```

### Monitor resource usage:
```bash
docker stats my-litellm-server
```

## 🛑 Stopping and Cleanup

### Stop the container:
```bash
docker stop my-litellm-server
```

### Remove the container:
```bash
docker rm my-litellm-server
```

> **NOTE:** `./kill-docker.sh` can be used to both stop and remove the container in one go.

### Using Docker Compose:
```bash
docker-compose down
```

## 🏥 Health Check

The container includes a health check endpoint:

```bash
curl http://localhost:4000/health
```

> **WARNING:** LiteLLM's `/health` endpoint also checks the responsiveness of the deployed Language Models, which **incurs extra costs !!!** Keep this in mind if you decide to set up an automatic health check for your deployment.

## 🏗️ Building from Source

If you need to build the image yourself, follow the instructions below.

> **NOTE:** You still need to set up the `.env` file as described in the beginning of the [Quick Start](#-quick-start) section.

### Direct Docker build

1. First build the image:
   ```bash
   docker build -t my-litellm-server .
   ```

2. Then run the container:
   ```bash
   docker run -d \
     --name my-litellm-server \
     -p 4000:4000 \
     --env-file .env \
     --restart unless-stopped \
     my-litellm-server
   ```
   > **NOTE:** To run in the foreground, remove the `-d` flag.

### Docker Compose build

Build and run by overlaying with the dev version of Compose setup:
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
```

This will map the current directory to the container.

> **NOTE:** To run in the foreground, remove the `-d` flag.

## 🔧 Troubleshooting

### Container won't start
1. Check if port 4000 is available: `lsof -i :4000`
2. Verify environment variables are set correctly
3. Check container logs: `docker logs -f my-litellm-server`

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
