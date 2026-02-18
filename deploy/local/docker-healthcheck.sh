#!/usr/bin/env bash
set -euo pipefail

HOST_PORT="${HOST_PORT:-5080}"
HEALTH_URL="${HEALTH_URL:-http://127.0.0.1:${HOST_PORT}/healthz}"
MAX_RETRIES="${MAX_RETRIES:-30}"
SLEEP_SECS="${SLEEP_SECS:-2}"

echo "[info] checking $HEALTH_URL"

for i in $(seq 1 "$MAX_RETRIES"); do
  if curl -fsS "$HEALTH_URL" >/dev/null 2>&1; then
    echo "[ok] service is healthy"
    exit 0
  fi
  sleep "$SLEEP_SECS"
done

echo "[error] health check failed after ${MAX_RETRIES} attempts"
exit 1
