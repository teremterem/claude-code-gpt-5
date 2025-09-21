#!/bin/bash
set -e
CONFIG_FILE="${LITELLM_CONFIG:-config.yaml}"
PROXY_PORT="${PROXY_PORT:-4000}"
echo ""
echo "🚀 Running Claude Code GPT-5 Proxy (via uv)..."
echo "📦 Config: ${CONFIG_FILE}"
echo ""
echo "📝 Usage with Claude Code:"
echo "   ANTHROPIC_BASE_URL=http://localhost:${PROXY_PORT} claude"
echo ""
uv run litellm --config "${CONFIG_FILE}" --port "${PROXY_PORT}" --host "0.0.0.0"
