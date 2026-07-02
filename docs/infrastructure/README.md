# UNTOLD Production Infrastructure

> **Full guide:** [deployment-guide.md](../deployment-guide.md) · **Global:** [global-deployment.md](../global-deployment.md) · **Checklist:** [production-checklist.md](../production-checklist.md)

## Quick start (Docker)

```bash
cp deploy/env/development.env.example .env
docker compose up -d --build
```

| Service | URL |
|---------|-----|
| Web (nginx) | http://localhost:8080 |
| API | http://localhost:8000 |
| Health | http://localhost:8000/health |
| Ready | http://localhost:8000/ready |
| Live | http://localhost:8000/live |
| Metrics | http://localhost:8000/metrics |

## Production compose

```bash
cp deploy/env/production.env.example .env
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
./deploy/scripts/smoke-test.sh
```

## Monitoring

```bash
docker compose -f docker-compose.yml -f docker-compose.monitoring.yml --profile monitoring up -d
```

| Service | URL |
|---------|-----|
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 |

## Logging (Loki)

```bash
docker compose -f docker-compose.yml -f docker-compose.logging.yml --profile logging up -d
```

## Kubernetes

```bash
cp deploy/kubernetes/secrets.example.yaml deploy/kubernetes/secrets.yaml
kubectl apply -k deploy/kubernetes
```

### Multi-region (production)

```bash
# EU primary
kubectl apply -k deploy/kubernetes/overlays/eu-primary --context eu

# US secondary (failover + geo traffic)
kubectl apply -k deploy/kubernetes/overlays/us-secondary --context us
```

See [Global Deployment](../global-deployment.md) for Cloudflare, DR, and observability.

## Cloudflare edge

```bash
cd deploy/cloudflare && wrangler deploy
```

## CI/CD

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `ci.yml` | PR / push | Tests + build |
| `cd.yml` | `main` / `v*` tags | GHCR push + deploy + smoke |
| `backup-verify.yml` | Weekly | Backup script validation |

## Health probes

| Path | Use |
|------|-----|
| `/live` | Liveness — process up |
| `/ready` | Readiness — DB + Redis |
| `/health` | Public health + version |

## Backups & DR

- **RPO:** 1h (WAL) / 24h (daily dump) · **RTO:** 1h (global) / 4h (single-region)
- Scripts: `deploy/scripts/backup.sh`, `restore.sh`, `dr-runbook.sh`, `global-failover.sh`
- Optional S3: `BACKUP_S3_URI=s3://bucket/path`

## Architecture

```
Internet → Cloudflare (CDN / WAF / LB / Worker)
              ├── Pages (SPA static)
              └── Regional K8s ingress
                    ├── Web (SPA fallback)
                    └── API (FastAPI) ──┬── PostgreSQL (+ replicas)
                          │             └── Redis
                    Celery workers ────────┘
                    Media → R2 + CDN_BASE_URL
                    
Observability: API → /metrics → Prometheus → Grafana
               API → OTLP → Collector → Tempo/Mimir
               Logs → Loki → Grafana
               Edge → Cloudflare Analytics + Logpush
```
