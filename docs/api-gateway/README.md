# UNTOLD API Gateway

Production API Gateway for third-party integrations.

## Features

- **REST API** — `/gateway/v1/*` and `/gateway/v2/*` (v2 uses `{ data, meta }` envelope)
- **GraphQL** — `/gateway/graphql`
- **Webhooks** — outbound event delivery with HMAC signatures
- **Rate limiting** — per API key tier (free / standard / enterprise) via Redis
- **Authentication** — JWT Bearer or `X-API-Key: unt_...`
- **API keys** — scoped permissions, tiers, expiration
- **Usage analytics** — request logs, latency, endpoint breakdown
- **OpenAPI** — `/gateway/openapi.json` and `/gateway/docs`
- **Versioning** — `X-API-Version` or `Accept-Version` header

## Quick start

```bash
# Create API key (Studio → API Gateway → API Keys)
curl -H "X-API-Key: unt_..." https://api.untold.com/gateway/v1/me

# List videos
curl -H "X-API-Key: unt_..." "https://api.untold.com/gateway/v1/videos?page=1"

# GraphQL
curl -X POST https://api.untold.com/gateway/graphql \
  -H "X-API-Key: unt_..." \
  -H "Content-Type: application/json" \
  -d '{"query": "{ me { email scopes } videos { total items { title } } }"}'
```

## Scopes

| Scope | Access |
|-------|--------|
| `videos.read` | List/get videos |
| `projects.read` | List/get productions |
| `analytics.read` | Analytics overview |
| `webhooks.manage` | Register webhooks |
| `graphql.query` | GraphQL endpoint |

## Webhook signature

Verify `X-UNTOLD-Signature` header: `HMAC-SHA256(secret, raw_body)`.

## Migration

```bash
cd backend && python -m alembic upgrade head
```

Revision: `036_api_gateway`
