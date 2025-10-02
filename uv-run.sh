#!/bin/bash

# Run claude-code-gpt-5 via uv

set -e
LITELLM_CONFIG="${LITELLM_CONFIG:-config.yaml}"
PROXY_PORT="${PROXY_PORT:-4000}"
echo ""
echo "🚀 Running Claude Code GPT-5 Proxy (via uv)..."
echo "📦 Config: ${LITELLM_CONFIG}"
echo ""
echo "📝 Usage with Claude Code:"
echo ""
echo "   ANTHROPIC_BASE_URL=http://localhost:${PROXY_PORT} claude"
echo ""
echo "      OR"
echo ""
echo "   ANTHROPIC_API_KEY=\"<LITELLM_MASTER_KEY>\" \\"
echo "   ANTHROPIC_BASE_URL=http://localhost:${PROXY_PORT} \\"
echo "   claude"
echo ""
echo ""
echo "Starting..."
uv run litellm --config "${LITELLM_CONFIG}" --port "${PROXY_PORT}" --host "0.0.0.0"
