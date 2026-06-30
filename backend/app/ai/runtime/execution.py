"""Resilient AI execution — retry, timeout, fallback."""

from __future__ import annotations

import logging
import time
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FuturesTimeoutError
from dataclasses import dataclass, field
from typing import Any, Callable, TypeVar

logger = logging.getLogger("untold.ai.runtime")

T = TypeVar("T")


@dataclass(frozen=True)
class ExecutionPolicy:
    max_retries: int = 2
    retry_backoff_seconds: float = 0.5
    timeout_seconds: float = 120.0
    fallback_provider_ids: tuple[str, ...] = field(default_factory=tuple)


def execute_with_resilience(
    operation: Callable[[], T],
    *,
    policy: ExecutionPolicy | None = None,
    on_retry: Callable[[int, Exception], None] | None = None,
) -> T:
    """Run *operation* with retries and optional timeout."""
    policy = policy or ExecutionPolicy()
    last_error: Exception | None = None

    for attempt in range(policy.max_retries + 1):
        try:
            if policy.timeout_seconds > 0:
                with ThreadPoolExecutor(max_workers=1) as pool:
                    future = pool.submit(operation)
                    return future.result(timeout=policy.timeout_seconds)
            return operation()
        except FuturesTimeoutError as exc:
            last_error = TimeoutError(f"AI operation timed out after {policy.timeout_seconds}s")
            logger.warning("AI operation timeout (attempt %s)", attempt + 1)
        except Exception as exc:
            last_error = exc
            if attempt < policy.max_retries:
                if on_retry:
                    on_retry(attempt + 1, exc)
                delay = policy.retry_backoff_seconds * (2**attempt)
                logger.warning("AI operation failed (attempt %s): %s — retry in %.1fs", attempt + 1, exc, delay)
                time.sleep(delay)
            else:
                logger.warning("AI operation failed after %s attempts: %s", attempt + 1, exc)

    assert last_error is not None
    raise last_error


def resolve_with_fallback_chain(
    capability: str,
    resolve_fn: Callable[[str | None], Any],
    *,
    preferred: str | None,
    fallback_ids: list[str],
    module: str | None = None,
) -> Any:
    """Try preferred provider, then explicit fallback chain, then registry default."""
    from app.ai.capability_registry import get_capability_registry

    reg = get_capability_registry()
    order: list[str | None] = []
    if preferred:
        order.append(preferred)
    order.extend(fallback_ids)
    order.append(None)

    seen: set[str] = set()
    for pid in order:
        key = pid or "__default__"
        if key in seen:
            continue
        seen.add(key)
        try:
            provider = resolve_fn(pid) if pid else reg.resolve(capability, module=module)
            if provider and getattr(provider, "is_available", lambda: True)():
                return provider
        except Exception as exc:
            logger.debug("Fallback skip %s/%s: %s", capability, pid, exc)
            continue
    raise RuntimeError(f"No provider available for capability '{capability}'")
