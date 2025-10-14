#!/bin/bash

set -e

COMPOSE_PROJECT_NAME="litellm-librechat"

# Change to the `librechat/` directory, where the docker-compose.yml for
# LibreChat file is located
cd "$(dirname "${BASH_SOURCE[0]}")"

if ! command -v docker >/dev/null 2>&1; then
  echo "❌ Docker is not installed or not available in PATH."
  exit 1
fi

DOCKER_COMPOSE=(docker compose)
if ! docker compose version >/dev/null 2>&1; then
  if command -v docker-compose >/dev/null 2>&1; then
    DOCKER_COMPOSE=(docker-compose)
  else
    echo "❌ docker compose plugin or docker-compose binary not found."
    exit 1
  fi
fi

COMPOSE_UID="${LIBRECHAT_UID:-0}"
COMPOSE_GID="${LIBRECHAT_GID:-0}"
COMPOSE_ENV_PREFIX=(env "UID=${COMPOSE_UID}" "GID=${COMPOSE_GID}")

print_command() {
  printf '%q ' "${COMPOSE_ENV_PREFIX[@]}" "${DOCKER_COMPOSE[@]}"
  for arg in "$@"; do
    printf '%q ' "$arg"
  done
  printf '\n'
}

run_compose() {
  print_command "$@"
  echo ""
  "${COMPOSE_ENV_PREFIX[@]}" "${DOCKER_COMPOSE[@]}" "$@"
}

echo ""
echo "🧹 Stopping any existing LibreChat stack..."
echo ""
run_compose -p "${COMPOSE_PROJECT_NAME}" down --remove-orphans || true
echo ""

# echo "⬇️  Pulling latest images..."
# echo ""
# run_compose -p "${COMPOSE_PROJECT_NAME}" pull
# echo ""

echo "🚀 Running LibreChat stack via Docker Compose..."
echo ""
echo "🧾 Compose project name: ${COMPOSE_PROJECT_NAME}"
echo ""
echo "🌐 HINT: Default Web UI URL (IF NOT CHANGED IN 'librechat/.env'):"
echo ""
echo "   http://localhost:3080"
echo ""
echo "▶️  Starting LibreChat stack in the foreground (Ctrl+C to stop)..."
echo ""
# Pass through any flags supplied to this script (e.g., --build, -d) to
# `docker compose up`.
run_compose -p "${COMPOSE_PROJECT_NAME}" up "$@"
echo ""
