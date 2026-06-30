# Architecture Decision Records (ADR)

We document significant architectural decisions using lightweight ADRs. Each record captures context, decision, and consequences.

## Format

```markdown
# ADR NNNN: Title
Status: Accepted | Superseded | Deprecated
Date: YYYY-MM-DD

## Context
## Decision
## Consequences
```

## Index

| ADR | Title | Status |
|-----|-------|--------|
| [0001](./0001-monorepo-three-surfaces.md) | Monorepo with three product surfaces | Accepted |
| [0002](./0002-fastapi-postgresql-stack.md) | FastAPI + PostgreSQL + Redis stack | Accepted |
| [0003](./0003-unified-ai-provider-layer.md) | Unified AI provider layer | Accepted |
| [0004](./0004-jwt-session-rbac.md) | JWT sessions and studio RBAC | Accepted |
| [0005](./0005-kubernetes-production-deployment.md) | Kubernetes for production deployment | Accepted |
| [0006](./0006-celery-async-workers.md) | Celery for async background work | Accepted |

## When to write an ADR

- New technology adoption (database, queue, cloud provider)
- Breaking API or schema strategy changes
- Security model changes
- Cross-team contracts (gateway, plugins)

## Related

- [Architecture](../architecture.md)
