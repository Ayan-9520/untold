# Production Checklist

Use before every production release and quarterly for ops review.

## Pre-deploy

### Secrets & configuration
- [ ] `SECRET_KEY` set (32+ chars, not default)
- [ ] `ENCRYPTION_KEY` set and **different** from `SECRET_KEY`
- [ ] `POSTGRES_PASSWORD` strong; not in git
- [ ] `CORS_ORIGINS` lists only production domains
- [ ] `TRUSTED_HOSTS` configured for production hostnames
- [ ] `DEBUG=false`, `ENVIRONMENT=production`
- [ ] `SEED_DATABASE=false`
- [ ] Vendor keys (OpenAI, Stripe, etc.) in secrets manager
- [ ] `GRAFANA_ADMIN_PASSWORD` changed from default

### Infrastructure
- [ ] TLS certificates valid (Ingress / CDN)
- [ ] DNS points to correct load balancer
- [ ] Postgres backups enabled (CronJob or `--profile backup`)
- [ ] `BACKUP_S3_URI` configured for off-site copies
- [ ] Redis persistence (`appendonly`) enabled
- [ ] Resource limits set (K8s or compose prod)

### CI/CD
- [ ] `ci.yml` green on release commit
- [ ] Docker images pushed to GHCR with version tag
- [ ] `KUBECONFIG_PRODUCTION` secret configured (if K8s)
- [ ] GitHub `production` environment requires approval

---

## Deploy

- [ ] Run migrations: `RUN_MIGRATIONS=true` on API only (entrypoint handles this)
- [ ] Rolling deploy: `kubectl rollout status` or `docker compose up -d --build`
- [ ] No errors in API startup logs
- [ ] Celery workers connected: `celery inspect ping`

---

## Post-deploy smoke tests

```bash
API_URL=https://api.yourdomain.com WEB_URL=https://yourdomain.com ./deploy/scripts/smoke-test.sh
```

- [ ] `GET /live` → `alive`
- [ ] `GET /ready` → `ready` (DB + Redis up)
- [ ] `GET /health` → `healthy`
- [ ] `GET /metrics` returns Prometheus text
- [ ] Web `/health` proxied OK
- [ ] Studio login works (`/studio/login`)
- [ ] Sample API auth flow (login + `/auth/me`)

---

## Monitoring

- [ ] Prometheus scraping `untold-api` job (`up==1`)
- [ ] Grafana dashboard loads (UNTOLD API)
- [ ] No active `UntoldApiDown` alerts
- [ ] Error rate < 1% (5xx)
- [ ] p95 latency < 2s

---

## Security

- [ ] Security headers present (`curl -I` on API and web)
- [ ] Rate limiting enabled (`RATE_LIMIT_ENABLED=true`)
- [ ] Admin/studio RBAC verified
- [ ] API docs disabled in production (`/docs` returns 404)

---

## Backups & DR

- [ ] Latest backup file exists and non-zero size
- [ ] `backup-verify.yml` workflow passing (weekly)
- [ ] DR runbook reviewed: `./deploy/scripts/dr-runbook.sh`
- [ ] Restore tested in staging within last 90 days

---

## Rollback plan

If smoke tests fail:

**Kubernetes:**
```bash
kubectl rollout undo deployment/untold-api -n untold
kubectl rollout undo deployment/untold-web -n untold
```

**Docker Compose:**
```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d api:previous-tag web:previous-tag
```

**Database:** Do not rollback migrations without DBA review. Restore from backup if schema incompatible.

---

## Sign-off

| Role | Name | Date |
|------|------|------|
| Deploy engineer | | |
| On-call | | |
