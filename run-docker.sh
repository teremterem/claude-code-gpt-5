#!/bin/bash

# Run claude-code-gpt-5 Docker container in the foreground
# This script pulls and runs the Docker image from GHCR

set -e

LITELLM_DOCKER_IMAGE="${LITELLM_DOCKER_IMAGE:-ghcr.io/teremterem/claude-code-gpt-5:latest}"
LITELLM_CONTAINER_NAME="${LITELLM_CONTAINER_NAME:-claude-code-gpt-5}"
LITELLM_PORT="${LITELLM_PORT:-4000}"

echo "🚀 Running Claude Code GPT-5 Proxy..."

# Stop and remove existing container if it exists
if docker ps -a --format 'table {{.Names}}' | grep -q "^${LITELLM_CONTAINER_NAME}$"; then
    echo "📦 Stopping existing container..."
    docker stop ${LITELLM_CONTAINER_NAME} || true
    docker rm ${LITELLM_CONTAINER_NAME} || true
fi

# Pull the latest image
echo "⬇️  Pulling latest image from GHCR..."
docker pull ${LITELLM_DOCKER_IMAGE}

# Run the container
echo ""
echo "▶️  Starting container..."
echo ""
echo "📝 Usage with Claude Code:"
echo ""
echo "   ANTHROPIC_BASE_URL=http://localhost:${LITELLM_PORT} claude"
echo ""
echo "      OR"
echo ""
echo "   ANTHROPIC_API_KEY=\"<LITELLM_MASTER_KEY>\" \\"
echo "   ANTHROPIC_BASE_URL=http://localhost:${LITELLM_PORT} \\"
echo "   claude"
echo ""
docker run \
    --name ${LITELLM_CONTAINER_NAME} \
    -p ${LITELLM_PORT}:4000 \
    --env-file .env \
    --restart unless-stopped \
    ${LITELLM_DOCKER_IMAGE}
