#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DOCKERFILE_PATH="${DOCKERFILE_PATH:-deploy/build/Dockerfile.tag.amd64}"
IMAGE_NAME="${IMAGE_NAME:-younghai/openmonitor}"
IMAGE_TAG="${IMAGE_TAG:-local-amd64}"
PLATFORM="${PLATFORM:-linux/amd64}"

echo "[info] root: $ROOT_DIR"
echo "[info] dockerfile: $DOCKERFILE_PATH"
echo "[info] image: ${IMAGE_NAME}:${IMAGE_TAG}"
echo "[info] platform: $PLATFORM"

docker build \
  --platform "$PLATFORM" \
  -t "${IMAGE_NAME}:${IMAGE_TAG}" \
  -f "$ROOT_DIR/$DOCKERFILE_PATH" \
  "$ROOT_DIR"

echo "[ok] built ${IMAGE_NAME}:${IMAGE_TAG}"
