# Runbook: Deployment Rollback

## When to rollback

- Smoke tests fail post-deploy
- Error rate spike > 5%
- Critical regression in studio or OTT
- Migration caused data issue

## Kubernetes rollback

### API

```bash
kubectl rollout history deployment/untold-api -n untold
kubectl rollout undo deployment/untold-api -n untold
kubectl rollout status deployment/untold-api -n untold
```

### Web

```bash
kubectl rollout undo deployment/untold-web -n untold
kubectl rollout status deployment/untold-web -n untold
```

### Workers

```bash
kubectl rollout undo deployment/untold-celery-worker -n untold
```

### Rollback to specific revision

```bash
kubectl rollout history deployment/untold-api -n untold
kubectl rollout undo deployment/untold-api -n untold --to-revision=3
```

### Pin to previous image tag

```bash
kubectl set image deployment/untold-api \
  api=ghcr.io/org/untold-api:v1.2.3 \
  -n untold
```

## Docker Compose rollback

```bash
# Rebuild from previous git tag
git checkout v1.2.3
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build api web

# Or pull previous image if tagged
docker compose pull api
docker compose up -d api
```

## Database rollback

Alembic downgrade is **risky** in production — prefer forward-fix migration.

If required:

```bash
cd backend
alembic downgrade -1   # one revision
alembic current
```

Coordinate with [Database Migration runbook](./database-migration.md).

## Post-rollback verification

```bash
API_URL=https://api.yourdomain.com ./deploy/scripts/smoke-test.sh
```

Check Grafana:
- Error rate normalized
- `up{job="untold-api"} == 1`

## CD pipeline rollback

If CD deployed bad tag:

1. Rollback via kubectl (above)
2. Re-tag or delete bad GHCR image
3. Fix forward on `main`; do not re-tag bad commit

## Related

- [Incident Response](./incident-response.md)
- [Deployment Guide](../deployment-guide.md)
