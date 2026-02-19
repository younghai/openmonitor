#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
IMAGE_NAME="${IMAGE_NAME:-younghai/openmonitor}"
IMAGE_TAG="${IMAGE_TAG:-local-amd64}"
CONTAINER_NAME="${CONTAINER_NAME:-openmonitor}"
HOST_PORT="${HOST_PORT:-5080}"
DATA_DIR="${DATA_DIR:-$ROOT_DIR/data/openmonitor}"
OPENOBSERVE_ORG="${OPENOBSERVE_ORG:-default}"
AUTO_BOOTSTRAP_DUMMY="${AUTO_BOOTSTRAP_DUMMY:-true}"

: "${ZO_ROOT_USER_EMAIL:?ERROR: Set ZO_ROOT_USER_EMAIL environment variable}"
: "${ZO_ROOT_USER_PASSWORD:?ERROR: Set ZO_ROOT_USER_PASSWORD environment variable}"

mkdir -p "$DATA_DIR"

echo "[info] container: $CONTAINER_NAME"
echo "[info] image: ${IMAGE_NAME}:${IMAGE_TAG}"
echo "[info] port: ${HOST_PORT}:5080"
echo "[info] data: $DATA_DIR"
echo "[info] org: $OPENOBSERVE_ORG"

if docker ps -a --format '{{.Names}}' | rg -qx "$CONTAINER_NAME"; then
  docker rm -f "$CONTAINER_NAME" >/dev/null
fi

docker run -d \
  --name "$CONTAINER_NAME" \
  --restart unless-stopped \
  -p "${HOST_PORT}:5080" \
  -v "${DATA_DIR}:/data" \
  -e ZO_DATA_DIR="/data" \
  -e ZO_ROOT_USER_EMAIL="$ZO_ROOT_USER_EMAIL" \
  -e ZO_ROOT_USER_PASSWORD="$ZO_ROOT_USER_PASSWORD" \
  "${IMAGE_NAME}:${IMAGE_TAG}" >/dev/null

echo "[ok] started $CONTAINER_NAME"

if [[ "$AUTO_BOOTSTRAP_DUMMY" == "true" ]]; then
  "$ROOT_DIR/deploy/local/docker-healthcheck.sh"
  if ! command -v python3 >/dev/null 2>&1; then
    echo "[error] python3 is required for demo bootstrap: deploy/local/bootstrap/seed_demo_content.py" >&2
    exit 1
  fi
  OPENOBSERVE_URL="http://127.0.0.1:${HOST_PORT}" \
  OPENOBSERVE_ORG="$OPENOBSERVE_ORG" \
  ZO_ROOT_USER_EMAIL="$ZO_ROOT_USER_EMAIL" \
  ZO_ROOT_USER_PASSWORD="$ZO_ROOT_USER_PASSWORD" \
  "$ROOT_DIR/deploy/local/bootstrap/seed_demo_content.py"
else
  echo "[hint] run: ./deploy/local/docker-healthcheck.sh"
fi
