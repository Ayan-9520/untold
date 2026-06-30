# System Architecture

UNTOLD is a full-stack sports storytelling ecosystem: consumer streaming (OTT), an internal production studio, and AI-powered content pipelines — unified by a single FastAPI backend and PostgreSQL data store.

## High-level architecture

```mermaid
flowchart TB
  subgraph Clients
    Browser[Web Browser]
    Mobile[Mobile PWA /app]
    StudioUI[Studio /studio]
    AIUI[AI Product /ai]
  end

  subgraph Edge
  CDN[CDN / Cloudflare]
  Ingress[Ingress / nginx]
  end

  subgraph Application
    WebSPA[React SPA — Vite]
    API[FastAPI API]
    GW[API Gateway /gateway]
    GQL[GraphQL /gateway/graphql]
    WS[WebSocket — live + studio]
    Celery[Celery Workers]
    Beat[Celery Beat]
  end

  subgraph Data
    PG[(PostgreSQL 16)]
    Redis[(Redis 7)]
    S3[(Object Storage)]
  end

  subgraph Observability
    Prom[Prometheus]
    Graf[Grafana]
    Loki[Loki + Promtail]
    OTEL[OTEL Collector]
  end

  Browser --> CDN --> Ingress
  Mobile --> CDN
  StudioUI --> Ingress
  AIUI --> Ingress
  Ingress --> WebSPA
  Ingress --> API
  API --> GW
  API --> GQL
  API --> WS
  API --> PG
  API --> Redis
  API --> S3
  Celery --> PG
  Celery --> Redis
  Beat --> Redis
  API -->|metrics| Prom
  Prom --> Graf
  Loki --> Graf
```

## Architectural principles

1. **Monorepo, multiple surfaces** — One repository; consumer web, studio, and AI are separate React route trees sharing components and API clients where appropriate.
2. **API-first** — All clients consume `/api/v1`; external integrators use `/gateway` with API keys.
3. **Domain-driven backend** — Business logic in `app/domain/`; HTTP thin in `app/api/v1/`; persistence in `app/models/`.
4. **Unified AI layer** — All LLM, image, video, voice, music, translation, and embedding calls route through `app/ai/` with retry, fallback, and cost telemetry.
5. **Production by default** — Health probes, structured logging, rate limits, security headers, migrations, and observability are built in.

## Request flow (authenticated API)

```mermaid
sequenceDiagram
  participant C as Client
  participant N as nginx / Ingress
  participant A as FastAPI
  participant M as Middleware
  participant D as Domain Service
  participant DB as PostgreSQL

  C->>N: HTTPS + Bearer JWT
  N->>A: Proxy request
  A->>M: CORS, rate limit, security headers
  M->>A: deps.get_current_user
  A->>DB: Validate session + load user
  A->>D: Business logic
  D->>DB: Query / commit
  D-->>A: Result
  A-->>C: JSON response
```

## Backend layers

| Layer | Path | Responsibility |
|-------|------|----------------|
| **HTTP** | `app/api/v1/` | Routes, validation, dependency injection |
| **Services** | `app/services/` | Orchestration, cross-domain workflows |
| **Domain** | `app/domain/` | Business rules, provider registries, RBAC |
| **AI runtime** | `app/ai/` | Provider resolution, invoke, cost tracking |
| **Models** | `app/models/` | SQLAlchemy ORM entities |
| **Workers** | `app/workers/` | Celery tasks (async jobs, pipelines) |
| **Gateway** | `app/gateway/` | External API, usage metering, GraphQL |
| **WebSocket** | `app/websocket/` | Live events, studio collaboration rooms |

## Frontend surfaces

```mermaid
flowchart LR
  App[App.jsx Router]
  App --> Web[WebRoutes /]
  App --> Mobile[MobileApp /app]
  App --> Studio[AdminApp /studio]
  App --> AI[AIApp /ai]
  Studio --> Features[admin/features/*]
  Web --> Pages[pages/*]
```

| Surface | Entry | Auth context |
|---------|-------|--------------|
| Website | `src/pages/`, `src/routes/WebRoutes.jsx` | `WebAuthContext` |
| Mobile | `src/app/MobileApp.jsx` | Shared web auth |
| Studio | `src/admin/AdminApp.jsx` | `AdminAuthContext` + studio JWT |
| AI | `src/ai/AIApp.jsx` | Product-specific (Phase 2) |

Legacy `/admin/*` URLs redirect to `/studio/*`.

## Core domain modules

| Domain | Backend | Studio UI |
|--------|---------|-----------|
| Content & OTT | `videos`, `streaming`, `watchlist` | Content, analytics |
| Live sports | `live`, WebSocket | Live components |
| News & magazine | `news`, `magazine` | Magazine page |
| Monetization | `payments`, `membership` | Revenue, subscriptions |
| Production studio | `studio_platform`, `*_studio` | Full studio nav |
| Workflows | `workflow_engine`, `production_pipeline` | Workflows, pipeline |
| Collaboration | `collaboration` | Collaboration workspace |
| Enterprise | `enterprise_security*` | Security dashboard |
| Plugins | `plugin_sdk` | Plugin marketplace |
| API Gateway | `api_gateway`, `/gateway` | API Gateway page |

## Data architecture

- **PostgreSQL** — System of record (users, content, studio projects, AI telemetry, enterprise audit).
- **Redis** — Rate limiting, Celery broker, live event pub/sub, response cache.
- **Object storage** — Media assets (local dev or S3-compatible in production).

See [Database](./database.md) for schema domains and migration policy.

## Async processing

```mermaid
flowchart LR
  API[API endpoint] -->|enqueue| Redis
  Redis --> Worker[Celery Worker]
  Worker --> PG[(PostgreSQL)]
  Worker --> AI[AI providers]
  Worker --> S3[(Storage)]
  Beat[Celery Beat] -->|schedule| Redis
```

Long-running work (publishing, localization, workflow steps, exports) runs in Celery workers — never block HTTP request threads.

## Security architecture

| Concern | Implementation |
|---------|----------------|
| Authentication | JWT access + refresh tokens; optional Google OAuth |
| Session revocation | `EnterpriseSession` + `validate_token_session()` |
| Authorization | Platform admin (`is_admin`), studio RBAC (`StudioRole` + permissions) |
| API keys | Gateway `unt_*` keys, SHA-256 hashed at rest |
| Transport | TLS at edge; HSTS in production |
| Application | CSP, rate limits, input validation, HTML sanitization |

See [Authentication](./authentication.md) and [Security Improvements](./security-improvements.md).

## Deployment topology

Production target: **Kubernetes** with optional Docker Compose for single-host deployments.

| Component | Replicas | Probes |
|-----------|----------|--------|
| API | 3+ | `/live`, `/ready` |
| Web (nginx) | 2+ | `/health` |
| Celery worker | 2+ | `celery inspect ping` |
| Celery beat | 1 | — |
| Postgres | 1 (managed HA recommended) | — |
| Redis | 1 (managed recommended) | `PING` |

See [Deployment](./deployment.md) and [Infrastructure](./infrastructure/README.md).

## Technology stack

| Layer | Technology |
|-------|------------|
| Frontend | React 19, Vite 6, Tailwind CSS 4, TanStack Query, React Router 7 |
| Backend | Python 3.11+, FastAPI, SQLAlchemy 2, Alembic, Pydantic v2 |
| Database | PostgreSQL 16 (+ pgvector for embeddings) |
| Cache / queue | Redis 7 |
| Workers | Celery |
| Observability | Prometheus, Grafana, Loki, OpenTelemetry |
| Containers | Docker, Kubernetes |
| CI/CD | GitHub Actions → GHCR → kubectl |

## Related documents

- [Folder Structure](./folder-structure.md)
- [API](./api.md)
- [AI](./ai.md)
- [ADR index](./adr/README.md)
