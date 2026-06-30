#!/bin/sh
# Post-deploy smoke tests — exit non-zero on failure
set -eu

API_URL="${API_URL:-http://localhost:8000}"
WEB_URL="${WEB_URL:-http://localhost:8080}"

echo "=== UNTOLD smoke test ==="
echo "API: $API_URL"
echo "Web: $WEB_URL"

curl -fsS "${API_URL}/live" | grep -q alive
echo "OK  GET /live"

curl -fsS "${API_URL}/ready" | grep -q ready
echo "OK  GET /ready"

curl -fsS "${API_URL}/health" | grep -q healthy
echo "OK  GET /health"

curl -fsS "${API_URL}/metrics" | head -1 >/dev/null
echo "OK  GET /metrics"

curl -fsS "${WEB_URL}/health" | grep -q healthy
echo "OK  GET web /health (proxied)"

echo "=== All smoke checks passed ==="
