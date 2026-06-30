# ADR 0004: JWT Sessions and Studio RBAC

**Status:** Accepted  
**Date:** 2025-09-01

## Context

UNTOLD needs stateless API scaling for OTT consumers, revocable sessions for enterprise customers, and fine-grained permissions for studio production workflows.

## Decision

**Authentication:**
- JWT access tokens (30 min) + refresh tokens (7 days)
- Bearer scheme on all protected routes
- `EnterpriseSession` table for revocation (`sid`/`jti` claims)
- `validate_token_session()` on API, gateway, and WebSocket

**Authorization:**
- Platform admin: `user.is_admin`
- Studio access: `user.studio_role` or project membership
- RBAC: `StudioRole` enum + permission map in `domain/studio/rbac.py`
- Dependency factories: `require_studio_permission()`, `require_project_permission()`

## Consequences

**Positive:**
- Horizontally scalable API (no server-side session store for basic JWT)
- Enterprise customers get revocable sessions
- Project-level roles support large production teams

**Negative:**
- Tokens in localStorage (XSS risk) — mitigated with CSP
- Legacy login tokens without sessions are not revocable until enterprise flow

## Alternatives considered

- **Server-side sessions only** — rejected; complicates horizontal scaling
- **OAuth only** — rejected as sole method; email/password required for studio
