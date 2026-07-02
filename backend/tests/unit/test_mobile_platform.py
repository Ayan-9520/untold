"""Unit tests for mobile platform."""

import pytest

from app.services.mobile_platform_service import MobilePlatformService
from app.services.mobile_push_service import MobilePushService


@pytest.mark.unit
def test_offline_manifest_studio():
    manifest = MobilePlatformService.offline_manifest(None, None, app_type="studio")
    assert manifest["app_type"] == "studio"
    assert "overview" in manifest["endpoints"]
    assert "approval_actions" in manifest["queues"]


@pytest.mark.unit
def test_offline_manifest_originals():
    manifest = MobilePlatformService.offline_manifest(None, None, app_type="originals")
    assert manifest["app_type"] == "originals"
    assert "home" in manifest["endpoints"]
    assert "watch_progress" in manifest["queues"]


@pytest.mark.unit
def test_device_dict_shape():
    class FakeDevice:
        id = 1
        app_type = "studio"
        platform = "ios"
        device_name = "iPhone"
        push_enabled = True
        last_seen_at = None
        created_at = None

    d = MobilePlatformService._device_dict(FakeDevice())
    assert d["id"] == 1
    assert d["app_type"] == "studio"
    assert d["platform"] == "ios"


@pytest.mark.unit
def test_push_service_notify_user_no_user():
    assert MobilePushService.notify_user(None, None, title="x") == 0
