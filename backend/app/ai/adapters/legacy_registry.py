"""Bridge legacy domain registries to the single capability registry."""

from __future__ import annotations

from typing import Any

from app.ai.bootstrap import ensure_bootstrapped, sync_domain_registry
from app.ai.capability_registry import get_capability_registry


def sync_legacy_registry(registry: Any, capability: str) -> None:
    """Populate a legacy domain registry from the canonical capability registry."""
    ensure_bootstrapped()
    sync_domain_registry(registry, capability)


def resolve_capability(
    capability: str,
    preferred: str | None = None,
    *,
    module: str | None = None,
) -> Any:
    """Resolve a provider via the canonical registry (shared resolution order)."""
    ensure_bootstrapped()
    return get_capability_registry().resolve(capability, preferred, module=module)
