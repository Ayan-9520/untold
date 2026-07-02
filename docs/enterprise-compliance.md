# Enterprise Compliance

Production-ready GDPR, SOC2, and ISO27001 controls for UNTOLD.

## Capabilities

| Area | Implementation |
|------|----------------|
| **GDPR** | Consent records, DSAR (access/erasure/portability), retention policies, privacy notice |
| **SOC2** | Access logs, audit trail, encryption checks, session management |
| **ISO27001** | Control mapping in compliance report, IP restrictions, RBAC |
| **Data retention** | Configurable policies + nightly Celery purge |
| **Consent** | `POST /api/v1/compliance/consent` (auth optional with email) |
| **Audit** | Existing `enterprise_audit_events` + compliance-tagged events |
| **Privacy** | Privacy requests workflow with 30-day SLA target |
| **Encryption** | Fernet at-rest (`ENCRYPTION_KEY`), TLS in production |
| **Access logs** | `compliance_access_logs` via middleware |
| **Reports** | `GET /api/v1/studio/platform/compliance/report` |

## API

### Public

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/compliance/privacy` | Privacy notice + policy version |
| GET | `/api/v1/compliance/policies` | Retention policy summary |
| POST | `/api/v1/compliance/consent` | Record consent |
| POST | `/api/v1/compliance/privacy-requests` | Submit DSAR |

### Admin (Studio)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/studio/platform/compliance/report` | Full compliance scorecard |
| GET | `/api/v1/studio/platform/compliance/policies` | List retention policies |
| PATCH | `/api/v1/studio/platform/compliance/policies/{key}` | Update policy |
| GET | `/api/v1/studio/platform/compliance/consents` | Consent audit trail |
| GET | `/api/v1/studio/platform/compliance/privacy-requests` | DSAR queue |
| POST | `/api/v1/studio/platform/compliance/privacy-requests/{id}/erasure` | Process erasure |
| POST | `/api/v1/studio/platform/compliance/privacy-requests/{id}/export` | Data export package |
| GET | `/api/v1/studio/platform/compliance/access-logs` | API access logs |
| POST | `/api/v1/studio/platform/compliance/retention/run` | Manual retention purge |

Enterprise Security `/studio/platform/security/compliance` returns the same extended report.

## Configuration

```bash
COMPLIANCE_ACCESS_LOG_ENABLED=true
COMPLIANCE_PRIVACY_POLICY_VERSION=1.0
ENCRYPTION_KEY=<openssl rand -hex 32>  # must differ from SECRET_KEY
```

## Default retention policies

| Policy | Category | Days | Auto-purge |
|--------|----------|------|------------|
| audit_logs | audit | 2555 (~7y) | No |
| access_logs | access | 365 | Yes |
| user_profile | pii | 365 | No |
| analytics_events | analytics | 90 | Yes |
| marketing_consent | marketing | 730 | Yes |
| privacy_requests | privacy | 1825 (5y) | No |

## Operations

- **Nightly purge:** Celery `untold.compliance_retention_purge` at 04:00 UTC
- **Migration:** `048_enterprise_compliance`
- **UI:** Studio → Enterprise Compliance (`/studio/compliance`)

## Related

- [Enterprise Security](./enterprise-security/README.md)
- [Authentication](./authentication.md)
- [Global Deployment](./global-deployment.md)
