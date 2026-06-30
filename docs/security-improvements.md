# Security Improvements

Focused hardening for JWT, RBAC, encryption, secrets, rate limits, CSP/HSTS, validation, sanitization, sessions, and API keys — without application redesign.

## Threat Analysis

| Threat | Vector | Mitigation |
|--------|--------|------------|
| **Token theft (XSS)** | AI HTML rendered via `innerHTML` | Client `sanitizeHtml()` strips scripts/event handlers |
| **Session fixation / reuse** | Refresh without session check | Refresh validates `sid`/`jti` and preserves session |
| **Revoked session access** | Gateway JWT bypassed session DB | `validate_token_session()` on gateway + WebSocket |
| **IDOR on projects** | Missing route-level RBAC | `require_project_permission("project.read")` on research workspace |
| **Credential stuffing** | Auth endpoints | Existing `10/minute` auth rate limits (unchanged) |
| **AI abuse / cost** | Unbounded generate calls | `30/minute` on AI/image generate + vectorstore |
| **Gateway rate-limit bypass** | Redis failure fail-open | Production returns 503 when Redis unavailable |
| **Clickjacking** | iframe embed | `X-Frame-Options: DENY`, CSP `frame-ancestors 'none'` |
| **MIME sniffing** | Malicious uploads/responses | `X-Content-Type-Options: nosniff` |
| **Downgrade attacks** | HTTP in production | HSTS via API middleware + Vercel headers |
| **Prompt injection** | Script tags in prompts | Pydantic validators reject `<script>` markup |
| **Weak encryption** | `SECRET_KEY` reused for Fernet | Production requires distinct `ENCRYPTION_KEY` |
| **Host header attacks** | Spoofed Host | Optional `TrustedHostMiddleware` via `TRUSTED_HOSTS` |
| **API key leakage** | Low-entropy keys | High-entropy `unt_*` keys, SHA-256 hash at rest, scoped access |

### Residual risks (documented, not redesigned)

- JWTs stored in `localStorage` (mitigate with CSP + XSS hygiene; httpOnly cookies are a future option)
- Legacy `/auth/login` tokens without DB sessions are not revocable until enterprise login is used
- API key hashes are SHA-256 without per-key salt (acceptable for 256-bit secrets)

---

## Modified Files

### Backend

| File | Change |
|------|--------|
| `backend/app/core/security.py` | JWT `iat`, `iss` claims; issuer validation on decode |
| `backend/app/core/session_security.py` | **New** — shared session revocation check |
| `backend/app/core/deps.py` | Uses `validate_token_session()` |
| `backend/app/core/config.py` | `jwt_issuer`, `trusted_hosts`, `rate_limit_ai`, CSP/HSTS settings; production `ENCRYPTION_KEY` validation |
| `backend/app/main.py` | Security headers middleware, tightened CORS, `TrustedHostMiddleware` |
| `backend/app/middleware/security_headers.py` | **New** — CSP, HSTS, frame denial |
| `backend/app/domain/gateway/auth.py` | Gateway JWT session validation; `hash_api_key()` helper |
| `backend/app/domain/gateway/rate_limit.py` | Fail closed in production on Redis errors |
| `backend/app/domain/security/sanitization.py` | **New** — input validation / HTML escape helpers |
| `backend/app/domain/security/compliance.py` | Accurate encryption + session compliance checks |
| `backend/app/services/auth_service.py` | Refresh preserves session; validates revocation |
| `backend/app/services/api_gateway_service.py` | Centralized API key hashing |
| `backend/app/websocket/studio.py` | Session check; studio users; project RBAC on rooms |
| `backend/app/schemas/ai_studio.py` | Prompt script-tag rejection |
| `backend/app/schemas/image_studio.py` | Prompt script-tag rejection |
| `backend/app/api/v1/ai_studio.py` | AI rate limits on generate/vectorstore |
| `backend/app/api/v1/image_studio.py` | Rate limit on image generate |
| `backend/app/api/v1/research_studio.py` | Route-level `project.read` permission |

### Frontend / Deploy

| File | Change |
|------|--------|
| `src/utils/sanitizeHtml.js` | **New** — allowlist HTML sanitizer |
| `src/admin/features/scripts/components/*.jsx` | Sanitize AI output before `innerHTML` |
| `deploy/docker/nginx.conf` | CSP, frame denial, referrer policy |
| `vercel.json` | CSP, HSTS, additional headers |

---

## Verification Checklist

### JWT & Session

- [ ] Login returns tokens with `iss: untold` and `iat` claim
- [ ] Refresh with revoked enterprise session returns `401`
- [ ] Refresh preserves `sid` — session row stays valid after refresh
- [ ] Gateway `Authorization: Bearer` rejects revoked session (`401`)
- [ ] WebSocket `/ws/studio?token=...` rejects revoked session (closes `4401`)

### RBAC

- [ ] User without `project.read` gets `403` on research workspace route
- [ ] Studio user with project access can join WebSocket room for that project
- [ ] Studio user cannot join room for unrelated project

### Encryption & Secrets

- [ ] Production boot fails if `ENCRYPTION_KEY` unset or equals `SECRET_KEY`
- [ ] Development still works with `ENCRYPTION_KEY` unset
- [ ] Security dashboard compliance shows `warn` for encryption when key not dedicated

### Rate Limits

- [ ] Auth endpoints return `429` after 10 requests/minute per IP
- [ ] `POST .../ai-studio/generate` returns `429` after 30 requests/minute
- [ ] Gateway returns `503` when Redis down in production

### CSP / HSTS / Headers

- [ ] `curl -I http://localhost:8000/health` includes security headers
- [ ] Production responses include `Strict-Transport-Security`
- [ ] Frontend via nginx includes CSP headers

### Input Validation & Sanitization

- [ ] AI generate with `<script>` in prompt returns `422`
- [ ] Script studio strips script tags from AI HTML output

### API Keys

- [ ] New keys work via `X-API-Key: unt_...` on `/gateway/*`
- [ ] Revoked keys return `401`

### Production deploy

```bash
ENCRYPTION_KEY=$(openssl rand -hex 32)   # must differ from SECRET_KEY
TRUSTED_HOSTS=yourdomain.com,api.yourdomain.com
```
