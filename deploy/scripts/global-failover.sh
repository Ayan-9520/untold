#!/bin/sh
# Global regional failover checklist — run during EU outage or DR drill
set -eu

REGION="${1:-}"
ACTION="${2:-check}"

echo "=== UNTOLD Global Failover ==="
echo "Region: ${REGION:-all} | Action: $ACTION"
echo ""

case "$ACTION" in
  check)
    echo "[1] Cloudflare LB pool health (manual): dashboard → Traffic → Load Balancing"
    echo "[2] EU API:  curl -sf https://api.untold.com/ready || echo FAIL"
    echo "[3] US API:  curl -sf https://us-lb.untold.com/ready || echo FAIL"
    echo "[4] Replication lag: check managed Postgres dashboard (< 30s)"
    ;;
  traffic-us)
    echo "[1] Set Cloudflare LB: disable eu-api pool OR set us-api priority 1"
    echo "[2] Verify: curl -sf https://api.untold.com/health"
    echo "[3] Monitor Grafana: error rate, latency, replication lag"
    ;;
  promote)
    echo "[1] Confirm EU primary is down — avoid split-brain"
    echo "[2] Promote US read replica to primary (provider CLI / console)"
    echo "[3] Update untold-secrets DATABASE_URL in US cluster to new primary"
    echo "[4] kubectl rollout restart deployment/untold-api -n untold --context us"
    echo "[5] Scale US celery-beat to 1; keep EU beat at 0"
    echo "[6] Run: API_URL=https://api.untold.com ./deploy/scripts/smoke-test.sh"
    echo "[7] Document incident; schedule EU rebuild as replica"
    ;;
  restore-eu)
    echo "[1] Rebuild EU Postgres as replica of current primary (US)"
    echo "[2] kubectl apply -k deploy/kubernetes/overlays/eu-primary --context eu"
    echo "[3] Re-enable eu-api pool in Cloudflare LB"
    echo "[4] Optional: switch primary back to EU during maintenance window"
    ;;
  *)
    echo "Usage: $0 [eu|us] [check|traffic-us|promote|restore-eu]"
    exit 1
    ;;
esac

echo ""
echo "RPO target: 1h (WAL) | RTO target: 1h"
echo "Full design: docs/global-deployment.md"
