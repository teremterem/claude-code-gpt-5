#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${SCRIPT_DIR}"

COMPOSE_FILE_DEFAULT="${PROJECT_ROOT}/librechat/docker-compose.yml"
COMPOSE_FILE="${COMPOSE_FILE:-${COMPOSE_FILE_DEFAULT}}"
COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-librechat}"
COMPOSE_WORKDIR_DEFAULT="${PROJECT_ROOT}/librechat/app"
COMPOSE_WORKDIR="${COMPOSE_WORKDIR:-${COMPOSE_WORKDIR_DEFAULT}}"

PORT="${PORT:-3080}"
RAG_PORT="${RAG_PORT:-8000}"

export PORT RAG_PORT

if [ ! -f "${COMPOSE_FILE}" ]; then
  echo "❌ Docker Compose file not found at ${COMPOSE_FILE}"
  exit 1
fi

if [ ! -d "${COMPOSE_WORKDIR}" ]; then
  echo "❌ Compose working directory not found at ${COMPOSE_WORKDIR}"
  exit 1
fi

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

print_command() {
  printf '+ '
  printf '%s ' "${DOCKER_COMPOSE[@]}"
  for arg in "$@"; do
    printf '%q ' "$arg"
  done
  printf '\n'
}

run_compose() {
  print_command "$@"
  "${DOCKER_COMPOSE[@]}" "$@"
}

echo "🚀 Running LibreChat stack via Docker Compose..."
echo "📁 Project root: ${PROJECT_ROOT}"
echo "📄 Compose file: ${COMPOSE_FILE}"
echo "🧾 Compose project name: ${COMPOSE_PROJECT_NAME}"
echo "📂 Compose working dir: ${COMPOSE_WORKDIR}"
echo ""
echo "🌐 Web UI:      http://localhost:${PORT}"
echo "🔌 RAG API:     http://localhost:${RAG_PORT}"
echo "📦 Data paths:  ${PROJECT_ROOT}/librechat"
echo ""

echo "🧹 Stopping any existing LibreChat stack..."
run_compose --project-directory "${COMPOSE_WORKDIR}" -p "${COMPOSE_PROJECT_NAME}" -f "${COMPOSE_FILE}" down --remove-orphans || true

echo "⬇️  Pulling latest images..."
run_compose --project-directory "${COMPOSE_WORKDIR}" -p "${COMPOSE_PROJECT_NAME}" -f "${COMPOSE_FILE}" pull

echo "▶️  Starting LibreChat stack in the foreground (Ctrl+C to stop)..."
echo ""
run_compose --project-directory "${COMPOSE_WORKDIR}" -p "${COMPOSE_PROJECT_NAME}" -f "${COMPOSE_FILE}" up
