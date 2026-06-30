# Authentication & Authorization

UNTOLD uses **JWT bearer tokens** for API authentication, optional **enterprise sessions** for revocation, and **role-based access control** for the production studio.

## Authentication flow

```mermaid
sequenceDiagram
  participant C as Client
  participant API as /api/v1/auth
  participant Auth as AuthService
  participant DB as PostgreSQL

  C->>API: POST /login { email, password }
  API->>Auth: validate credentials
  Auth->>DB: load user, check active
  Auth->>DB: create EnterpriseSession (optional)
  Auth-->>C: { access_token, refresh_token, token_type }
  C->>API: GET /me (Bearer access_token)
  API->>DB: validate session + user
  API-->>C: UserResponse
```

## Token model

| Token | Type claim | TTL (default) | Use |
|-------|------------|---------------|-----|
| Access | `type: access` | 30 minutes | API requests |
| Refresh | `type: refresh` | 7 days | Obtain new access token |

JWT claims include:

- `sub` — user ID
- `iat` — issued at
- `iss` — issuer (`untold`, configurable)
- `sid` / `jti` — session identifiers (enterprise flows)

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/register` | Create account |
| POST | `/api/v1/login` | Email/password login (alias at root) |
| POST | `/api/v1/auth/register` | Same as register |
| POST | `/api/v1/auth/login` | Same as login |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| POST | `/api/v1/auth/google` | Google ID token login |
| GET | `/api/v1/auth/me` | Current user profile |
| GET | `/api/v1/auth/studio/me` | Studio user + role |

## Client usage

```http
POST /api/v1/auth/login
Content-Type: application/json

{ "email": "user@example.com", "password": "..." }
```

```http
GET /api/v1/auth/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

Frontend storage:

- **Website:** `WebAuthContext` → `localStorage`
- **Studio:** `AdminAuthContext` → `localStorage` (`studio_token`)

> **Security note:** Tokens in `localStorage` require strict CSP and XSS hygiene. HttpOnly cookies are a future enhancement (see [Security Improvements](./security-improvements.md)).

## Session revocation

Enterprise login creates `EnterpriseSession` rows. On each authenticated request:

1. `decode_token()` validates signature, expiry, issuer
2. `validate_token_session()` checks session not revoked
3. Refresh tokens preserve `sid` and re-validate session

Revocation paths:

- Admin forces logout via enterprise security dashboard
- Session expiry
- Password reset (policy-dependent)

Gateway and WebSocket paths also call `validate_token_session()`.

## Authorization layers

```mermaid
flowchart TB
  Request[Incoming request]
  Request --> AuthN{Valid JWT?}
  AuthN -->|No| R401[401 Unauthorized]
  AuthN -->|Yes| Layer{Which layer?}
  Layer --> Admin[is_admin?]
  Layer --> Studio[studio_role + permission]
  Layer --> Project[project member role]
  Admin --> R403[403 Forbidden]
  Studio --> R403
  Project --> OK[200 OK]
```

### Platform admin

`get_current_admin` — requires `user.is_admin == True`.

Used for: `/admin`, analytics admin, revenue reports.

### Studio access

`get_current_studio_user` — requires `is_admin` OR assigned `studio_role`.

### Studio RBAC

Roles (`StudioRole`):

| Role | Typical use |
|------|-------------|
| `admin` | Full studio + settings |
| `producer` | Project ownership, approvals |
| `researcher` | Research workspace |
| `writer` | Scripts |
| `editor` | Timeline, storyboard |
| `designer` | Assets, storyboard |
| `publisher` | CMS, scheduling |
| `viewer` | Read-only |

Permissions are defined in `app/domain/studio/rbac.py`:

```python
require_studio_permission("script.edit")
require_project_permission("project.read", project_id)
```

Sample permissions: `project.create`, `research.edit`, `script.approve`, `publish.schedule`, `admin.manage`.

### API Gateway keys

External integrators authenticate with:

```http
X-API-Key: unt_<256-bit-secret>
```

Keys are SHA-256 hashed at rest; scopes limit accessible gateway routes. Managed via `/studio/api-gateway`.

## Enterprise security

Additional features (migration `037`):

| Feature | Tables / endpoints |
|---------|-------------------|
| SAML/OIDC IdP | `enterprise_idp_providers` |
| MFA (TOTP) | `enterprise_mfa_enrollments` |
| IP allow/deny | `enterprise_ip_rules` |
| Secrets vault | `enterprise_secrets` (Fernet encrypted) |
| Audit log | `enterprise_audit_events` |

UI: `/studio/security`  
API: `/api/v1/enterprise-security`, `/enterprise-security-auth`

Requires distinct `ENCRYPTION_KEY` in production (not equal to `SECRET_KEY`).

## Google OAuth

`POST /api/v1/auth/google` with `{ "id_token": "..." }`.

Links or creates user by `google_id`. Configure Google OAuth client in environment.

## Rate limiting

Auth endpoints: **10 requests/minute** per IP (`RATE_LIMIT_AUTH`).

Brute-force mitigation — do not disable in production.

## Configuration

| Variable | Purpose |
|----------|---------|
| `SECRET_KEY` | JWT signing (32+ chars) |
| `ENCRYPTION_KEY` | Fernet field encryption (production required) |
| `JWT_ISSUER` | Token issuer claim |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access TTL |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh TTL |
| `RATE_LIMIT_ENABLED` | Global rate limit toggle |

## Default development accounts

| Account | Email | Password | Access |
|---------|-------|----------|--------|
| Admin | `admin@untold.com` | `ChangeMe123!` | Platform + studio |
| User | `alex@untold.com` | `Untold123!` | Consumer |

**Change immediately** in any shared or production environment.

## Related documents

- [Security Improvements](./security-improvements.md)
- [Enterprise Security](./enterprise-security/README.md)
- [Admin Guide](./admin-guide.md)
- [ADR 0004: JWT session RBAC](./adr/0004-jwt-session-rbac.md)
