#!/bin/bash

# Deploy claude-code-gpt-5 Docker container
# This script pulls and runs the Docker image from GHCR

set -e

DOCKER_IMAGE="ghcr.io/teremterem/claude-code-gpt-5:latest"
CONTAINER_NAME="claude-code-gpt-5"
PORT="4000"

echo "🚀 Deploying Claude Code GPT-5 Proxy..."

# Stop and remove existing container if it exists
if docker ps -a --format 'table {{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "📦 Stopping existing container..."
    docker stop ${CONTAINER_NAME} || true
    docker rm ${CONTAINER_NAME} || true
fi

# Pull the latest image
echo "⬇️  Pulling latest image from GHCR..."
docker pull ${DOCKER_IMAGE}

# Run the container
echo "▶️  Starting container..."
docker run -d \
    --name ${CONTAINER_NAME} \
    --platform linux/amd64 \
    -p ${PORT}:4000 \
    -e OPENAI_API_KEY="${OPENAI_API_KEY}" \
    -e ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY}" \
    -e OPENAI_ENFORCE_ONE_TOOL_CALL_PER_RESPONSE=true \
    --restart unless-stopped \
    ${DOCKER_IMAGE}

echo "✅ Claude Code GPT-5 Proxy deployed successfully!"
echo "🔗 Proxy URL: http://localhost:${PORT}"
echo "📊 Health check: curl http://localhost:${PORT}/health"
echo ""
echo "📝 Usage with Claude Code:"
echo "   ANTHROPIC_BASE_URL=http://localhost:${PORT} claude --model gpt-5-reason-medium"
echo ""
echo "🛑 To stop: docker stop ${CONTAINER_NAME}"
echo "🔍 To view logs: docker logs -f ${CONTAINER_NAME}"
