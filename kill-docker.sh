#!/bin/bash

# Stop claude-code-gpt-5 Docker container

set -e

LITELLM_CONTAINER_NAME="${LITELLM_CONTAINER_NAME:-claude-code-gpt-5}"

echo "❌ Killing Claude Code GPT-5 Proxy..."

if docker ps -a --format 'table {{.Names}}' | grep -q "^${LITELLM_CONTAINER_NAME}$"; then
    echo "📦 Stopping container..."
    docker stop ${LITELLM_CONTAINER_NAME} || true
    echo "🗑️  Removing container..."
    docker rm ${LITELLM_CONTAINER_NAME} || true
    echo "✅ ${LITELLM_CONTAINER_NAME} stopped and removed."
else
    echo "ℹ️  No container named ${LITELLM_CONTAINER_NAME} found."
fi
