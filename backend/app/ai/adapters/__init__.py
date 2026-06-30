"""Backward-compatible adapters over the canonical AI layer."""

from app.ai.adapters.legacy_registry import resolve_capability, sync_legacy_registry

__all__ = ["resolve_capability", "sync_legacy_registry"]
