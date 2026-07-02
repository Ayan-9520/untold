"""Unit tests for enterprise AI agent platform."""

import pytest

from app.domain.agents.registry import AGENT_PERMISSIONS, BACKEND_AGENT_REGISTRY, permission_allowed
from app.services.agent_platform_service import AgentPlatformService


@pytest.mark.unit
def test_agent_permissions_catalog():
    assert "ai.generate" in AGENT_PERMISSIONS
    assert "memory.read" in AGENT_PERMISSIONS
    assert "schedule.manage" in AGENT_PERMISSIONS


@pytest.mark.unit
def test_permission_allowed_memory_wildcard():
    assert permission_allowed(["ai.generate"], "memory.read") is True
    assert permission_allowed(["ai.generate"], "communicate.send") is False
    assert permission_allowed(["memory.read"], "memory.read") is True


@pytest.mark.unit
def test_sample_agents_registered():
    assert "research" in BACKEND_AGENT_REGISTRY
    assert "publishing" in BACKEND_AGENT_REGISTRY


@pytest.mark.unit
def test_sdk_docs_shape():
    docs = AgentPlatformService.sdk_docs()
    assert docs["title"] == "UNTOLD Agent SDK"
    assert "backend" in docs
    assert "permissions" in docs
    assert "agent.run.completed" in docs["events"]
