# ADR 0006: Celery for Async Background Work

**Status:** Accepted  
**Date:** 2025-08-01

## Context

AI generation, publishing pipelines, localization, workflow steps, and exports exceed HTTP timeout budgets (minutes, not seconds).

## Decision

Use **Celery** with **Redis** broker:

- Workers: `app/workers/tasks.py`
- Beat scheduler: periodic jobs (publishing, cleanup)
- API enqueues tasks; returns job ID for polling/WebSocket updates
- Health check: `celery inspect ping`

Production: 2+ worker replicas; separate beat singleton.

## Consequences

**Positive:**
- API remains responsive under heavy AI load
- Retries and task routing per queue (extensible)
- Industry-standard Python async pattern

**Negative:**
- Operational complexity (worker monitoring, queue backlog alerts)
- Task idempotency required for safe retries

## Alternatives considered

- **FastAPI BackgroundTasks** — rejected; not durable, no scaling
- **Dramatiq / RQ** — viable; Celery chosen for beat scheduler and ecosystem
