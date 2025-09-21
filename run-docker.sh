#!/bin/bash

# Run claude-code-gpt-5 Docker container in the foreground
# This script pulls and runs the Docker image from GHCR

set -e

PROXY_DOCKER_IMAGE="${PROXY_DOCKER_IMAGE:-ghcr.io/teremterem/claude-code-gpt-5:latest}"
PROXY_CONTAINER_NAME="${PROXY_CONTAINER_NAME:-claude-code-gpt-5}"
PROXY_PORT="${PROXY_PORT:-4000}"

echo "🚀 Running Claude Code GPT-5 Proxy..."

# Stop and remove existing container if it exists
if docker ps -a --format 'table {{.Names}}' | grep -q "^${PROXY_CONTAINER_NAME}$"; then
    echo "📦 Stopping existing container..."
    docker stop ${PROXY_CONTAINER_NAME} || true
    docker rm ${PROXY_CONTAINER_NAME} || true
fi

# Pull the latest image
echo "⬇️  Pulling latest image from GHCR..."
docker pull ${PROXY_DOCKER_IMAGE}

# Run the container
echo ""
echo "▶️  Starting container..."
echo ""
echo "📝 Usage with Claude Code:"
echo "   ANTHROPIC_BASE_URL=http://localhost:${PROXY_PORT} claude"
echo ""
docker run \
    --name ${PROXY_CONTAINER_NAME} \
    -p ${PROXY_PORT}:4000 \
    --env-file .env \
    --restart unless-stopped \
    ${PROXY_DOCKER_IMAGE}
