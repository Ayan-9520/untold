"""Viewer profile and live reminder tests."""

import pytest
from unittest.mock import MagicMock

from app.models.viewer import ViewerProfile
from app.services.viewer_profile_service import LiveReminderService, ViewerProfileService


def test_device_limits_defined():
    from app.services.viewer_profile_service import DEVICE_LIMITS

    assert DEVICE_LIMITS["free"] == 1
    assert DEVICE_LIMITS["vip"] == 4


def test_ensure_primary_creates_profile():
    user = MagicMock(id=1, full_name="Test User", preferences_json=None)
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None
    db.add = MagicMock()
    db.commit = MagicMock()
    db.refresh = MagicMock(side_effect=lambda row: row)

    profile = ViewerProfileService.ensure_primary(db, user)
    assert profile.is_primary is True
    db.add.assert_called_once()


def test_live_reminder_idempotent():
    user = MagicMock(id=1)
    db = MagicMock()
    existing = MagicMock(id=5, match_id="m1", match_title="Final")
    db.query.return_value.filter.return_value.first.return_value = existing

    result = LiveReminderService.set_reminder(db, user, "m1", "Final")
    assert result is existing
    db.add.assert_not_called()
