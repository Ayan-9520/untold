# AI Architecture

Single provider layer for all UNTOLD AI capabilities with backward-compatible domain facades.

## Overview

```
app/ai/
├── capability_registry.py   # Canonical CapabilityRegistry (single registry)
├── bootstrap.py             # ensure_bootstrapped() — registers all providers once
├── config.py                # AIConfig — keys, defaults, enabled providers
├── adapters/
│   └── legacy_registry.py   # sync_legacy_registry(), resolve_capability()
├── runtime/
│   ├── execution.py         # retry, timeout, fallback chain
│   ├── cost_tracking.py     # token/cost telemetry on results
│   └── invoke.py            # invoke_llm(), invoke_provider_method(), embed_texts()
├── prompts/
│   └── versioning.py        # PromptVersionService
└── providers/
    ├── factory.py           # ProviderFactory (public API)
    ├── registry.py          # AIRegistry (public API)
    └── llm.py               # LLM vendor implementations
```

Domain packages (`app/domain/*/providers/registry.py`) remain the **public import path** for studio services. They delegate resolution and invocation to the canonical layer.

## Capabilities

| Capability    | Registry accessor              | Invoke method        |
|---------------|--------------------------------|----------------------|
| LLM           | `get_provider_registry()`      | `generate()`         |
| Image         | `get_image_registry()`         | `generate()`         |
| Video         | `get_video_registry()`         | `generate()`         |
| Voice         | `get_voice_registry()`         | `generate()`, `preview()` |
| Music         | `get_music_registry()`         | `generate()`, `preview()` |
| Translation   | `get_translation_registry()`   | `translate()`        |
| Embeddings    | `get_embeddings_registry()`    | `embed()`            |
| Vector store  | `get_vectorstore_registry()`   | `upsert()`, `search()` |

Unified entry points (unchanged):

- `from app.ai import get_ai_registry, get_provider_factory`
- `GET /api/v1/ai-studio/overview` → `get_ai_registry().overview()`

## Resolution order

`CapabilityRegistry.resolve()` uses `AIConfig` per capability:

1. Explicit `preferred` provider (if enabled)
2. Capability default (`AIConfig.default_for(capability)`)
3. Remaining enabled providers (sorted)
4. LLM: `media_stub`, then `demo`; other capabilities: `demo`

## Resilience

All invocations through `app/ai/runtime/invoke.py` use `execute_with_resilience()`:

- **Retry**: 2 retries, exponential backoff (0.5s base)
- **Timeout**: 120s default (60s for embeddings)
- **Cost metadata**: attached to `result.meta["telemetry"]` via `attach_cost_metadata()`

Configure per-call by passing a custom `ExecutionPolicy` when calling runtime helpers directly.

## Prompt versioning

`PromptVersionService` (`app/ai/prompts/versioning.py`) versions rows in `ai_prompt_library`:

- `prompt_key` — stable key `{module}:{slug}`
- `version` — monotonic integer per key
- `is_current` — one active version per key

```python
from app.ai.prompts import PromptVersionService

text, version = PromptVersionService.resolve_text(db, "script", "Outline v1", variables={"topic": "..."})
row = PromptVersionService.create_version(db, module="script", title="Outline v1", prompt_template="...")
```

Existing rows without `prompt_key` still resolve by `title` until backfilled.

## Migration steps

### 1. Deploy code (no breaking API changes)

Studio services continue importing domain registries; behavior is routed through `app/ai`.

### 2. Run database migration

```bash
cd backend
alembic upgrade head   # applies 038_ai_prompt_versioning
```

Adds `prompt_key`, `version`, `is_current` to `ai_prompt_library`.

### 3. Backfill prompt keys (optional)

```sql
UPDATE ai_prompt_library
SET prompt_key = module || ':' || lower(replace(left(title, 120), ' ', '-'))
WHERE prompt_key IS NULL;
```

### 4. Verify bootstrap

```bash
cd backend
python -c "from app.ai import ensure_bootstrapped; ensure_bootstrapped(); print('OK')"
```

### 5. New provider registration (going forward)

Register **once** in `app/ai/bootstrap.py`:

```python
reg.register("image", MyImageProvider())
```

Domain registries pick it up via `sync_legacy_registry()` on first access. Do not register vendors in both `bootstrap.py` and domain `get_*_registry()` factories.

### 6. Deprecation path (future)

| Legacy | Replacement |
|--------|-------------|
| Direct vendor imports in services | `get_*_registry()` or `get_capability_registry()` |
| Duplicate registration in domain `get_*_registry()` | `app/ai/bootstrap.py` only |
| `bootstrap_legacy_llm_registry()` | `sync_legacy_registry(registry, "llm")` |

## Backward compatibility

- **Import paths**: `get_provider_registry`, `get_image_registry`, `get_ai_registry`, `get_provider_factory` unchanged
- **Method signatures**: `resolve()`, `generate()`, `embed()`, `translate()`, `upsert()`, `search()` unchanged
- **HTTP APIs**: No router changes required
- **Config**: Existing `Settings` / env vars (`AI_ENABLED_PROVIDERS`, `IMAGE_ENABLED_PROVIDERS`, etc.) still drive resolution via `AIConfig`
- **Results**: `provider` and `meta` fields still set on generation results; `meta.telemetry` added when absent

## Adding a new capability provider

1. Implement provider in `app/domain/<capability>/providers/`
2. Register in `app/ai/bootstrap.py`
3. Add env keys to `Settings` and `AIConfig` if needed
4. Extend `CAPABILITIES` in `app/ai/providers/base.py` only if introducing a **new** capability type
