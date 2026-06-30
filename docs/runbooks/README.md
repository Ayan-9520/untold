# Operational Runbooks

Step-by-step procedures for on-call engineers and platform operators.

## Runbook index

| Runbook | When to use |
|---------|-------------|
| [Incident Response](./incident-response.md) | Outage, elevated errors, security event |
| [Backup & Restore](./backup-restore.md) | Scheduled backup verification, data recovery |
| [Deployment Rollback](./deployment-rollback.md) | Failed deploy, bad release |
| [Database Migration](./database-migration.md) | Schema changes, failed migration |

## Quick diagnostics

```bash
# Health
curl -fsS https://api.yourdomain.com/live
curl -fsS https://api.yourdomain.com/ready
curl -fsS https://api.yourdomain.com/health

# Smoke suite
API_URL=https://api.yourdomain.com WEB_URL=https://yourdomain.com ./deploy/scripts/smoke-test.sh

# Kubernetes
kubectl get pods -n untold
kubectl logs -n untold deployment/untold-api --tail=100
kubectl rollout status deployment/untold-api -n untold

# Docker Compose
docker compose ps
docker compose logs -f api --tail=100
```

## Escalation

| Severity | Definition | Response time |
|----------|------------|---------------|
| **SEV-1** | Complete outage or data loss risk | 15 minutes |
| **SEV-2** | Major feature degraded | 1 hour |
| **SEV-3** | Minor degradation | Next business day |
| **SEV-4** | Cosmetic / non-urgent | Backlog |

## Key contacts

Configure in your organization's on-call rotation:

- **Platform on-call** — infrastructure, deploys
- **Backend on-call** — API, database, workers
- **Security** — breach, credential leak

## Related documents

- [Production Checklist](../production-checklist.md)
- [Deployment Guide](../deployment-guide.md)
- [DR script](../../deploy/scripts/dr-runbook.sh)
