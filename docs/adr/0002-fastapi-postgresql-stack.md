# ADR 0002: FastAPI + PostgreSQL + Redis Stack

**Status:** Accepted  
**Date:** 2025-06-01

## Context

UNTOLD requires a typed REST API, relational data for studio workflows, caching, rate limiting, and real-time pub/sub for live sports and collaboration.

## Decision

| Layer | Technology |
|-------|------------|
| API framework | FastAPI (Python 3.11+) |
| ORM | SQLAlchemy 2.0 |
| Migrations | Alembic |
| Database | PostgreSQL 16 (+ pgvector) |
| Cache / broker | Redis 7 |

## Consequences

**Positive:**
- FastAPI auto-generates OpenAPI; Pydantic validation
- Postgres handles complex studio relations and JSON
- Redis supports rate limits, Celery, live WebSocket fan-out

**Negative:**
- Python GIL limits CPU-bound work in API process — offloaded to Celery
- Redis single point of failure — use managed HA in production

## Alternatives considered

- **Node/NestJS** — rejected; AI/ML ecosystem stronger in Python
- **MongoDB** — rejected; studio workflows need ACID and joins
