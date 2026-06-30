"""AI capability registry unit tests."""

import pytest

from app.ai.bootstrap import ensure_bootstrapped
from app.ai.capability_registry import get_capability_registry


@pytest.mark.unit
def test_capability_registry_bootstraps_llm_providers():
    ensure_bootstrapped()
    providers = get_capability_registry().list_providers("llm")
    ids = {p["id"] for p in providers}
    assert "demo" in ids
    assert len(providers) >= 2


@pytest.mark.unit
def test_capability_registry_resolve_demo_llm():
    ensure_bootstrapped()
    provider = get_capability_registry().resolve("llm", "demo", module="script")
    assert provider.id == "demo"
