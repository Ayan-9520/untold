# ADR 0001: Monorepo with Three Product Surfaces

**Status:** Accepted  
**Date:** 2025-06-01

## Context

UNTOLD serves multiple audiences: public OTT consumers, internal production teams, and a future AI SaaS product. Teams need shared API contracts, branding, and release coordination without maintaining separate repositories.

## Decision

Use a **single monorepo** with three React route trees in `src/`:

| Surface | Path | Package |
|---------|------|---------|
| Consumer web + mobile | `/`, `/app` | `src/pages`, `src/app` |
| UNTOLD Studio | `/studio` | `src/admin` |
| UNTOLD AI | `/ai` | `src/ai` |

One FastAPI backend (`backend/`) serves all surfaces. Legacy `/admin` redirects to `/studio`.

## Consequences

**Positive:**
- Shared components, API clients, and design tokens
- Atomic cross-surface changes in one PR
- Single CI pipeline

**Negative:**
- Larger repository; longer clone times
- Frontend bundle requires code-splitting / lazy routes
- Clear ownership boundaries needed per surface

## Alternatives considered

- **Multi-repo** — rejected due to API drift and duplicate UI code
- **Micro-frontends** — deferred; complexity not justified at current scale
