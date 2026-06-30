# ADR 0005: Kubernetes for Production Deployment

**Status:** Accepted  
**Date:** 2026-01-01

## Context

Production requires horizontal scaling, rolling deploys, health probes, secrets management, and operational tooling (backups, monitoring).

## Decision

- **Primary production target:** Kubernetes (`deploy/kubernetes/`)
- **Alternative:** Docker Compose with prod overrides for single-host / early prod
- **CI/CD:** GitHub Actions → GHCR → `kubectl set image`
- **Probes:** `/live` (liveness), `/ready` (readiness)
- **Observability:** Prometheus ServiceMonitor, optional Loki stack

## Consequences

**Positive:**
- Rolling updates with zero-downtime path
- HPA for API and workers
- CronJob for daily backups

**Negative:**
- K8s operational overhead for small teams
- Compose remains supported for simpler deployments

## Alternatives considered

- **Railway/Fly only** — supported as hybrid; not primary for full studio stack
- **ECS** — viable; K8s chosen for manifest portability

See [Deployment Guide](../deployment-guide.md).
