# Runbook: Backup & Restore

## Overview

| Metric | Value |
|--------|-------|
| Schedule | Daily 03:00 UTC (K8s CronJob) |
| RPO | 24 hours |
| RTO | 4 hours |
| Format | `pg_dump` → gzip → optional S3 |

## Backup procedure

### Manual backup

```bash
./deploy/scripts/backup.sh
```

### With S3 off-site copy

```bash
export BACKUP_S3_URI=s3://your-bucket/untold-backups
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
./deploy/scripts/backup.sh
```

### Kubernetes CronJob

```bash
kubectl get cronjob -n untold
kubectl get jobs -n untold --sort-by=.metadata.creationTimestamp
```

### Verify backup integrity

```bash
ls -lh ${BACKUP_DIR:-/backups}
gunzip -t /backups/untold_*.sql.gz
```

Weekly CI job `backup-verify.yml` validates scripts.

## Restore procedure

> **Warning:** Restore is destructive — overwrites the target database.

### 1. Scale down writers

```bash
kubectl scale deployment untold-api --replicas=0 -n untold
kubectl scale deployment untold-celery-worker --replicas=0 -n untold
```

Or for Compose:

```bash
docker compose stop api celery_worker celery_beat
```

### 2. Restore database

```bash
./deploy/scripts/restore.sh /backups/untold_YYYYMMDD_HHMMSS.sql.gz
```

### 3. Run migrations

```bash
cd backend && alembic upgrade head
# Or set RUN_MIGRATIONS=true on API startup once
```

### 4. Scale up

```bash
kubectl scale deployment untold-api --replicas=3 -n untold
kubectl scale deployment untold-celery-worker --replicas=2 -n untold
```

### 5. Verify

```bash
./deploy/scripts/smoke-test.sh
```

## Point-in-time recovery

For managed Postgres (RDS, Cloud SQL):

1. Use provider PITR to new instance
2. Update `DATABASE_URL` in secrets
3. Restart API pods
4. Run smoke tests

## Disaster recovery

Full DR checklist:

```bash
./deploy/scripts/dr-runbook.sh
```

## Related

- [Incident Response](./incident-response.md)
- [Database Migration](./database-migration.md)
