#!/bin/sh
# Disaster recovery checklist runner (manual failover steps)
set -eu

echo "=== UNTOLD Disaster Recovery ==="
echo "1. Verify backup integrity: ls -lh \${BACKUP_DIR:-/backups}"
echo "2. Scale down writers: kubectl scale deployment untold-api --replicas=0 -n untold"
echo "3. Restore DB: ./deploy/scripts/restore.sh <latest-backup>"
echo "4. Run migrations: alembic upgrade head"
echo "5. Scale up API: kubectl scale deployment untold-api --replicas=3 -n untold"
echo "6. Verify health: ./deploy/scripts/smoke-test.sh"
echo "7. Notify stakeholders and document incident"
echo ""
echo "RTO target: 4 hours | RPO target: 24 hours (daily backups)"
echo "For automated K8s DR see deploy/kubernetes/backup-cronjob.yaml"
