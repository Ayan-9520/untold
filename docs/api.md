# API Reference

UNTOLD exposes a versioned REST API at `/api/v1`, health/metrics at the root, an external **API Gateway** at `/gateway`, and optional **GraphQL** at `/gateway/graphql`.

## Base URLs

| Environment | Base URL |
|-------------|----------|
| Local | `http://localhost:8000` |
| Docker Compose | `http://localhost:8000` (API), `http://localhost:8080` (web proxy) |
| Production | `https://api.yourdomain.com` |

All versioned routes are prefixed with `/api/v1` unless noted.

## API surface map

```mermaid
flowchart TB
  Root[FastAPI app]
  Root --> Health[/live /ready /health /metrics]
  Root --> V1[/api/v1/*]
  Root --> GW[/gateway/*]
  Root --> GQL[/gateway/graphql]
  Root --> WS[WebSocket]

  V1 --> Auth[auth users]
  V1 --> OTT[videos categories watchlist streaming]
  V1 --> Live[live news magazine community]
  V1 --> Biz[analytics payments membership admin]
  V1 --> Studio[studio_* *_studio workflow_*]
  V1 --> Ent[enterprise_security* plugin_sdk api_gateway]
```

## Module index

### Platform

| Prefix / router | Tag | Auth | Description |
|-----------------|-----|------|-------------|
| `/auth`, `/register`, `/login` | Auth | Mixed | Registration, login, refresh, `/me` |
| `/users` | Users | JWT | Profile management |
| `/health`, `/live`, `/ready` | Health | Public | Probes (root level, not under `/api/v1`) |
| `/metrics` | Metrics | Public | Prometheus scrape endpoint |

### Consumer (OTT)

| Prefix | Auth | Description |
|--------|------|-------------|
| `/videos` | Public / tiered | Catalog, detail, search |
| `/categories` | Public | Content categories |
| `/watchlist` | JWT | User watchlist |
| `/streaming` | JWT / tier | Playback, progress |
| `/live` | Public | Live matches, events |
| `/news` | Public | News feed |
| `/magazine` | Mixed | E-magazine editions |
| `/community` | Mixed | Fan engagement |
| `/membership` | JWT | Subscription status |
| `/payments` | JWT | Checkout; webhooks separate |

### Studio production

| Prefix | Auth | Description |
|--------|------|-------------|
| `/studio` | Studio JWT | Core studio operations |
| `/studio-platform` | Studio + RBAC | Projects, tasks, members |
| `/research-studio` | Studio + RBAC | Research workspace |
| `/script-studio` | Studio + RBAC | Script writing + AI |
| `/storyboard-studio` | Studio + RBAC | Storyboard generation |
| `/image-studio` | Studio + RBAC | AI image generation |
| `/video-studio` | Studio + RBAC | AI video generation |
| `/voice-studio` | Studio + RBAC | Voice synthesis |
| `/music-studio` | Studio + RBAC | Music generation |
| `/shorts-studio` | Studio + RBAC | Short-form content |
| `/seo-studio` | Studio + RBAC | SEO variants |
| `/translation-studio` | Studio + RBAC | Localization |
| `/asset-library` | Studio + RBAC | Media asset management |
| `/timeline-editor` | Studio + RBAC | Timeline sessions |
| `/publishing-cms` | Studio + RBAC | CMS publishing |
| `/publishing-agent` | Studio + RBAC | AI publishing agent |
| `/production-pipeline` | Studio + RBAC | Quick pipeline runs |
| `/workflow-engine` | Studio + RBAC | Workflow definitions & runs |
| `/ai-studio` | Studio | AI provider overview |
| `/ai-pipeline` | Studio | AI pipeline orchestration |
| `/ai-cost` | Studio admin | Cost budgets and reports |
| `/studio-analytics` | Studio | Production analytics |
| `/studio-admin` | Studio admin | Settings, flags, backups |
| `/collaboration` | Studio + RBAC | Real-time collaboration docs |

### Enterprise & extensions

| Prefix | Auth | Description |
|--------|------|-------------|
| `/enterprise-security` | Studio admin | IdP, MFA, IP rules, audit |
| `/enterprise-security-auth` | Mixed | Enterprise login flows |
| `/api-gateway` | Studio admin | Key management (admin UI) |
| `/plugin-sdk` | Studio | Plugin registry |
| `/agent-marketplace` | Studio | Agent marketplace |

### External gateway

| Path | Auth | Description |
|------|------|-------------|
| `/gateway/v1/*` | `X-API-Key` | Rate-limited external REST proxy |
| `/gateway/openapi.json` | Public | Gateway OpenAPI 3.1 spec |
| `/gateway/docs` | Public | Gateway Swagger UI |
| `/gateway/graphql` | API key / JWT | GraphQL entry |

See [API Gateway](./api-gateway/README.md).

## Authentication

All protected routes expect:

```http
Authorization: Bearer <access_token>
```

Studio routes additionally enforce `studio_role` or project-level RBAC. Gateway routes use:

```http
X-API-Key: unt_<key>
```

See [Authentication](./authentication.md).

## Common response shapes

### Success

```json
{
  "id": 1,
  "title": "UNTOLD: The Revolution"
}
```

### Application error

```json
{
  "detail": "Studio access required",
  "code": "FORBIDDEN"
}
```

### Validation error (422)

```json
{
  "detail": [{ "loc": ["body", "email"], "msg": "field required", "type": "missing" }],
  "code": "VALIDATION_ERROR"
}
```

## Pagination

List endpoints that support pagination return:

```json
{
  "items": [],
  "total": 120,
  "page": 1,
  "page_size": 20,
  "has_more": true
}
```

Query params: `page` (1-based), `page_size` (max varies by endpoint).

## Rate limiting

| Tier | Default limit | Endpoints |
|------|---------------|-----------|
| Auth | 10/minute | `/auth/login`, `/register`, `/refresh` |
| AI generate | 30/minute | Image/video/voice generate |
| Default | Configurable | All other routes |

Exceeded limits return `429 Too Many Requests`.

## Versioning

- **URL prefix:** `/api/v1` — breaking changes require `/api/v2`.
- **Gateway:** `X-API-Version` / `Accept-Version` headers supported on gateway routes.
- **OpenAPI:** App version in `settings.app_version`; gateway spec versioned independently.

## WebSocket

| Path | Purpose |
|------|---------|
| `/ws/live/{match_id}` | Live match event stream |
| `/ws/studio/{project_id}` | Studio collaboration presence |

Connections require valid JWT; studio rooms enforce project RBAC.

## Error codes

| Code | HTTP | Meaning |
|------|------|---------|
| `UNAUTHORIZED` | 401 | Missing or invalid token |
| `FORBIDDEN` | 403 | Insufficient role/permission |
| `NOT_FOUND` | 404 | Resource missing |
| `VALIDATION_ERROR` | 422 | Request body invalid |
| `DATABASE_ERROR` | 500 | DB failure (sanitized in prod) |
| `INTERNAL_ERROR` | 500 | Unhandled exception |

## Interactive documentation

| Environment | REST docs | Gateway docs |
|-------------|-----------|--------------|
| Development | `http://localhost:8000/docs` | `http://localhost:8000/gateway/docs` |
| Production | Disabled | Configure per policy |

See [OpenAPI](./openapi.md) for export and CI integration.

## Client SDKs

Frontend clients use Axios wrappers in:

- `src/api/` — consumer API
- `src/admin/api/adminApi.js` — studio API

No official external SDK is published; generate from OpenAPI spec.

## Related documents

- [OpenAPI](./openapi.md)
- [Authentication](./authentication.md)
- [Developer Guide](./developer-guide.md)
