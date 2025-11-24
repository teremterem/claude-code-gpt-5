#!/bin/bash

# Run my-litellm-server via uv

set -e
LITELLM_CONFIG="${LITELLM_CONFIG:-config.yaml}"
LITELLM_PORT="${LITELLM_PORT:-4000}"
echo ""
echo "🚀 Running My LiteLLM Server (via uv)..."
echo "📦 Config: ${LITELLM_CONFIG}"
echo ""
echo "Starting..."
uv run litellm --config "${LITELLM_CONFIG}" --port "${LITELLM_PORT}" --host "0.0.0.0"
