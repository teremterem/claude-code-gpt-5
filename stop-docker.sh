#!/bin/bash

# Stop claude-code-gpt-5 Docker container

set -e

PROXY_CONTAINER_NAME="${PROXY_CONTAINER_NAME:-claude-code-gpt-5}"

echo "❌ Stopping Claude Code GPT-5 Proxy..."

if docker ps -a --format 'table {{.Names}}' | grep -q "^${PROXY_CONTAINER_NAME}$"; then
    echo "📦 Stopping container..."
    docker stop ${PROXY_CONTAINER_NAME} || true
    echo "🗑️  Removing container..."
    docker rm ${PROXY_CONTAINER_NAME} || true
    echo "✅ ${PROXY_CONTAINER_NAME} stopped and removed."
else
    echo "ℹ️  No container named ${PROXY_CONTAINER_NAME} found."
fi
