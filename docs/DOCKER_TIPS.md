# Docker Tips for the LiteLLM Server

This guide explains how to deploy the LiteLLM Server using Docker. It DOES NOT cover the deployment of the LibreChat UI - for the latter see the [README](../README.md).

## 🐳 Dummy Docker Images

LiteLLM Server that contains the Yoda example:
```
ghcr.io/teremterem/litellm-server-yoda:latest
```

LibreChat image with the config for the Yoda example baked in:
```
ghcr.io/teremterem/librechat-yoda:latest
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
   # LITELLM_MASTER_KEY=strong-key-that-you-generated

   # More settings (see .env.template for details)
   ...
   ```

## 🏗️ Building from Source

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

## 🏥 Health Check

The container includes a health check endpoint:

```bash
curl http://localhost:4000/health
```

> **WARNING:** LiteLLM's `/health` endpoint also checks the responsiveness of the deployed Language Models, which **incurs extra costs !!!** Keep this in mind if you decide to set up an automatic health check for your deployment.

## 🔧 Troubleshooting

### Container won't start
1. Check if port 4000 is available: `lsof -i :4000`
2. Verify environment variables are set correctly
3. Check container logs: `docker logs -f my-litellm-server`

### Authentication issues
1. Verify your API keys are valid and have sufficient credits
2. Check if OpenAI requires identity verification if you are trying to use GPT-5 (see [README.md](../README.md), section "GPT-5 caveat")

## 🔐 Security Notes

- Keep your API keys secure and never commit them to version control
- Use environment variables or Docker secrets for sensitive data
- Consider running the container in a restricted network environment
- Regularly update the image to get security patches
