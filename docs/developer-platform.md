# UNTOLD Public Developer Platform

Production-ready public API for third-party integrations.

## Capabilities

| Feature | Location |
|---------|----------|
| **REST API** | `/gateway/v1`, `/gateway/v2` |
| **GraphQL** | `/gateway/graphql` |
| **Webhooks** | Signed outbound events |
| **SDK** | `src/developer-sdk/index.js` |
| **Rate limits** | Per-key tiers (free / standard / enterprise) |
| **API keys** | `unt_live_*` (production), `unt_sandbox_*` (sandbox) |
| **Developer portal** | `/developers` |
| **Usage analytics** | `/api/v1/developer/usage/*` |
| **Versioning** | `X-API-Version`, v1 flat JSON, v2 envelope |
| **Sandbox** | `/gateway/sandbox/v1` — sample data only |

## Self-service API

Prefix: `/api/v1/developer` (requires user JWT)

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/register` | Create developer account |
| `GET` | `/me` | Account profile |
| `GET` | `/docs` | Platform documentation JSON |
| `GET` | `/scopes` | Scopes, tiers, webhook events |
| `GET` | `/sandbox` | Sandbox environment info |
| `GET/POST/DELETE` | `/keys` | Manage API keys |
| `GET` | `/usage/overview` | Usage summary |
| `GET` | `/usage/timeseries` | Daily request chart |
| `GET` | `/usage/endpoints` | Top endpoints |
| `GET/POST/DELETE` | `/webhooks` | Webhook management |

## Authentication

```bash
# Production REST
curl -H "X-API-Key: unt_live_YOUR_KEY" http://localhost:8000/gateway/v1/videos

# Sandbox
curl -H "X-API-Key: unt_sandbox_YOUR_KEY" http://localhost:8000/gateway/sandbox/v1/videos

# GraphQL
curl -X POST http://localhost:8000/gateway/graphql \
  -H "X-API-Key: unt_live_YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query":"{ me { email scopes } }"}'
```

## SDK

```javascript
import { UntoldClient } from '../developer-sdk';

const client = new UntoldClient({
  apiKey: process.env.UNTOLD_API_KEY,
  environment: 'production',
  version: 'v2',
});

const videos = await client.videos.list({ page: 1 });
```

## Database (migration `047`)

- `developer_accounts` — self-service developer profiles
- `studio_api_keys.environment` — `sandbox` | `production`
- `api_gateway_usage_logs.environment` — per-request environment tag

## Studio admin

Internal operators can still manage all keys via **Studio → API Gateway** (`/studio/api-gateway`).

## Production checklist

- [ ] Run `alembic upgrade head` (through `047`)
- [ ] Enable Redis for rate limiting (`RATE_LIMIT_ENABLED=true`)
- [ ] Wire FCM/APNs not required — webhooks use HTTPS delivery
- [ ] Restrict CORS for `/developers` portal in production
- [ ] Monitor `api_gateway_usage_logs` volume and retention
