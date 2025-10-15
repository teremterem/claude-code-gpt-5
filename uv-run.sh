#!/bin/bash

# Run claude-code-gpt-5 via uv

set -e
LITELLM_CONFIG="${LITELLM_CONFIG:-config.yaml}"
PROXY_PORT="${PROXY_PORT:-4000}"
echo ""
echo "🚀 Running Claude Code GPT-5 Proxy (via uv)..."
echo "📦 Config: ${LITELLM_CONFIG}"
echo ""
echo "Starting..."
uv run litellm --config "${LITELLM_CONFIG}" --port "${PROXY_PORT}" --host "0.0.0.0"
