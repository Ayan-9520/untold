# ADR 0007: Multi-Tenant SaaS for UNTOLD Studio

**Status:** Accepted  
**Date:** 2026-06-30

## Context

UNTOLD Studio operated as a single global tenant with project-scoped RBAC. Customers require isolated organizations, team/workspace structure, per-tenant billing, branding, and audit isolation for production SaaS.

## Decision

Introduce a four-level hierarchy:

**Organization → Team → Workspace → Project**

- **Organization** is the billing and isolation boundary (`organization_id` on projects, API keys, audit).
- **PostgreSQL RLS** on `productions` and `tenant_audit_events` using session variable `app.current_organization_id`.
- **App-layer RBAC** with `OrganizationRole` separate from project `StudioRole`.
- **Backward compatibility:** default org `untold-default` backfills existing data; optional `X-Organization-ID` header defaults to user's primary org.

## Consequences

**Positive:**
- True multi-tenant SaaS with seat limits, plan limits, white-label branding
- Tenant-scoped audit and storage key prefixes
- Existing studio APIs continue working with automatic org resolution

**Negative:**
- Clients should adopt org/workspace headers for multi-org users
- RLS not yet on all studio tables (assets, AI) — phase 4 hardening
- Migration required before deploy

## Alternatives considered

- **Schema-per-tenant** — rejected; operational complexity
- **Workspace-only (no org)** — rejected; insufficient for billing isolation
