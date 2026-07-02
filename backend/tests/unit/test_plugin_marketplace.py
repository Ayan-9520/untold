"""Unit tests for plugin marketplace extensions."""

import pytest

from app.domain.plugins.events import STUDIO_EVENTS
from app.domain.plugins.hooks import HOOK_POINTS
from app.services.plugin_sdk_service import PluginSdkService


@pytest.mark.unit
def test_plugin_hooks_catalog():
    assert "workflow.before_node" in HOOK_POINTS
    assert "dashboard.widgets" in HOOK_POINTS
    assert "seo.format_title" in HOOK_POINTS


@pytest.mark.unit
def test_plugin_events_catalog():
    assert "workflow.run.started" in STUDIO_EVENTS
    assert "publish.completed" in STUDIO_EVENTS
    assert "ai.job.completed" in STUDIO_EVENTS


@pytest.mark.unit
def test_sdk_docs_structure():
    docs = PluginSdkService.sdk_docs()
    assert docs["title"] == "UNTOLD Plugin SDK"
    assert "backend" in docs
    assert "frontend" in docs
    assert "events" in docs
    assert "hooks" in docs
