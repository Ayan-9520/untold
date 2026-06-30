"""Studio RBAC unit tests."""

import pytest

from app.domain.studio.enums import StudioRole
from app.domain.studio.rbac import role_has_permission


@pytest.mark.unit
@pytest.mark.parametrize(
    ("role", "permission", "expected"),
    [
        (StudioRole.ADMIN, "project.delete", True),
        (StudioRole.VIEWER, "project.read", True),
        (StudioRole.VIEWER, "project.delete", False),
        (StudioRole.RESEARCHER, "research.edit", True),
        (StudioRole.WRITER, "research.edit", False),
    ],
)
def test_role_has_permission(role, permission, expected):
    assert role_has_permission(role, permission) is expected
