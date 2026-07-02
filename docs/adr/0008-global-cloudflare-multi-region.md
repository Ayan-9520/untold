# ADR 0008: Global Deployment with Cloudflare and Multi-Region Kubernetes

**Status:** Accepted  
**Date:** 2026-07-01

## Context

UNTOLD serves a global OTT audience, studio operators, and public API consumers. Single-region deployment creates latency for distant users and a single point of failure. We already run Kubernetes manifests, Prometheus/Grafana, backups, and HPA (`deploy/kubernetes/`). We need a production global architecture covering CDN, edge compute, multi-region compute, DR, and observability.

## Decision

1. **Edge:** Cloudflare as the global entry point — DNS, CDN, WAF, Load Balancer, and Workers.
2. **Static:** Cloudflare Pages (or R2 + CDN) for the React SPA; immutable asset caching at edge.
3. **API:** Two Kubernetes regions — **EU primary** (writes + workers) and **US secondary** (read replica + failover).
4. **Routing:** Cloudflare Load Balancer with geo steering and `/ready` health checks; optional Edge Worker for cacheable GETs.
5. **Data:** Managed PostgreSQL with cross-region read replica; WAL/PITR to S3/R2; daily `pg_dump` CronJob retained.
6. **Media:** Cloudflare R2 with `CDN_BASE_URL` (already supported in storage layer).
7. **Scale:** Existing API HPA (3–12); add worker HPA and PodDisruptionBudgets.
8. **Observability:** Prometheus + OTEL + Loki per region; federate to central Grafana; Cloudflare analytics for edge.

## Consequences

**Positive:**
- Sub-100ms static delivery globally via CDN
- Automatic origin failover when EU pool unhealthy
- Aligns with existing R2/CDN code paths and K8s manifests
- Clear RPO/RTO targets and scripted failover

**Negative:**
- Cross-region Postgres replication lag during failover (brief read-only or stale reads)
- Celery beat must remain single-leader (EU) — duplicate beat causes duplicate jobs
- Cloudflare + multi-cluster operational complexity
- `DATABASE_READ_URL` read splitting not yet implemented in application code (US serves full traffic only after promotion)

## Alternatives considered

| Alternative | Why not primary |
|-------------|-----------------|
| **Single region + CDN only** | No compute failover; high API latency for distant users |
| **Active-active writes both regions** | Requires conflict resolution; overkill for current scale |
| **AWS CloudFront + ALB** | Valid; team standardized on Cloudflare for R2, WAF, Workers cohesion |
| **Fly.io multi-region alone** | Good for API; doesn't replace CDN/edge for static at same maturity |

## Implementation

- Design doc: [global-deployment.md](../global-deployment.md)
- Config: `deploy/cloudflare/`, `deploy/kubernetes/overlays/`, `deploy/env/global-production.env.example`
