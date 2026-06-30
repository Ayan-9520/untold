# ADR 0003: Unified AI Provider Layer

**Status:** Accepted  
**Date:** 2025-12-01

## Context

Studio modules (script, image, video, voice, music, translation, research) each had separate provider registries. This caused duplicate registration, inconsistent retry/fallback behavior, and fragmented cost tracking.

## Decision

Introduce canonical layer at `app/ai/`:

- `CapabilityRegistry` — single registry for all AI capabilities
- `bootstrap.py` — one-time provider registration
- `runtime/invoke.py` — retry, timeout, fallback, cost telemetry
- Domain registries (`app/domain/*/providers/`) delegate via `sync_legacy_registry()`

Prompt versioning via `PromptVersionService` on `ai_prompt_library`.

## Consequences

**Positive:**
- Consistent resilience policies across all AI calls
- Central cost tracking and budgets
- Backward-compatible imports for existing studio services

**Negative:**
- Indirection layer adds learning curve
- Must register providers only in `bootstrap.py` to avoid duplicates

## Migration

Deploy code → run migration `038_ai_prompt_versioning` → optional prompt key backfill.

See [AI Architecture](../ai-architecture.md).
