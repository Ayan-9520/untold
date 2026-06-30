# Enterprise Security

Production-grade security for UNTOLD Studio.

## Features

| Area | Description |
|------|-------------|
| **SSO / OAuth / OIDC** | Google, Azure AD, custom OAuth providers |
| **SAML** | Okta-style SAML federation with SP metadata |
| **2FA (TOTP)** | Authenticator apps + backup codes |
| **RBAC** | Studio role permissions (existing + dashboard) |
| **Audit logs** | Tamper-evident events with SHA-256 checksums |
| **Encryption** | Fernet encryption for secrets at rest |
| **Secrets vault** | Encrypted storage with rotation |
| **Sessions** | Track, revoke, and validate active sessions |
| **IP restrictions** | Allow/deny CIDR rules for Studio access |
| **Compliance** | SOC2, GDPR, HIPAA, ISO27001 readiness scoring |

## Auth endpoints

```
POST /api/v1/auth/security/login          # Password + MFA challenge flow
POST /api/v1/auth/security/mfa/verify     # Complete MFA login
GET  /api/v1/auth/security/sso/{slug}/start
POST /api/v1/auth/security/sso/{slug}/callback
POST /api/v1/auth/security/sso/{slug}/saml/acs
```

## Admin API

```
GET  /studio/platform/security/overview
GET  /studio/platform/security/compliance
GET  /studio/platform/security/audit
GET  /studio/platform/security/idp
POST /studio/platform/security/mfa/setup
GET  /studio/platform/security/sessions
POST /studio/platform/security/ip-rules
POST /studio/platform/security/secrets
```

## Migration

```bash
cd backend && python -m alembic upgrade head
```

Revision: `037_enterprise_security`

## Studio UI

**Studio → Enterprise Security** (`/studio/security`)
