"""UNTOLD Studio — role-based access control."""

from app.domain.studio.enums import StudioRole

# Permission → roles allowed
PERMISSIONS: dict[str, frozenset[StudioRole]] = {
    "studio.access": frozenset(StudioRole),
    "project.create": frozenset({StudioRole.ADMIN, StudioRole.PRODUCER}),
    "project.read": frozenset(StudioRole),
    "project.update": frozenset({
        StudioRole.ADMIN, StudioRole.PRODUCER, StudioRole.RESEARCHER,
        StudioRole.WRITER, StudioRole.EDITOR, StudioRole.DESIGNER,
    }),
    "project.delete": frozenset({StudioRole.ADMIN, StudioRole.PRODUCER}),
    "research.edit": frozenset({StudioRole.ADMIN, StudioRole.PRODUCER, StudioRole.RESEARCHER}),
    "research.approve": frozenset({StudioRole.ADMIN, StudioRole.PRODUCER}),
    "script.edit": frozenset({StudioRole.ADMIN, StudioRole.PRODUCER, StudioRole.WRITER}),
    "script.approve": frozenset({StudioRole.ADMIN, StudioRole.PRODUCER}),
    "storyboard.edit": frozenset({StudioRole.ADMIN, StudioRole.PRODUCER, StudioRole.EDITOR, StudioRole.DESIGNER}),
    "storyboard.approve": frozenset({StudioRole.ADMIN, StudioRole.PRODUCER}),
    "asset.upload": frozenset({StudioRole.ADMIN, StudioRole.PRODUCER, StudioRole.EDITOR, StudioRole.DESIGNER}),
    "asset.read": frozenset(StudioRole),
    "asset.manage": frozenset({StudioRole.ADMIN, StudioRole.PRODUCER, StudioRole.EDITOR, StudioRole.DESIGNER}),
    "timeline.edit": frozenset({StudioRole.ADMIN, StudioRole.PRODUCER, StudioRole.EDITOR}),
    "timeline.export": frozenset({StudioRole.ADMIN, StudioRole.PRODUCER, StudioRole.EDITOR, StudioRole.PUBLISHER}),
    "ai.generate": frozenset({
        StudioRole.ADMIN, StudioRole.PRODUCER, StudioRole.RESEARCHER,
        StudioRole.WRITER, StudioRole.EDITOR, StudioRole.DESIGNER,
    }),
    "publish.schedule": frozenset({StudioRole.ADMIN, StudioRole.PRODUCER, StudioRole.PUBLISHER}),
    "publish.approve": frozenset({StudioRole.ADMIN, StudioRole.PRODUCER}),
    "team.manage": frozenset({StudioRole.ADMIN, StudioRole.PRODUCER}),
    "settings.manage": frozenset({StudioRole.ADMIN}),
    "analytics.read": frozenset({
        StudioRole.ADMIN, StudioRole.PRODUCER, StudioRole.PUBLISHER, StudioRole.VIEWER,
    }),
    "admin.read": frozenset({StudioRole.ADMIN, StudioRole.PRODUCER}),
    "admin.manage": frozenset({StudioRole.ADMIN}),
}


def role_has_permission(role: StudioRole | str, permission: str) -> bool:
    allowed = PERMISSIONS.get(permission)
    if not allowed:
        return False
    if isinstance(role, str):
        try:
            role = StudioRole(role)
        except ValueError:
            return False
    return role in allowed


def resolve_user_studio_role(is_admin: bool, member_role: str | None) -> StudioRole:
    if is_admin:
        return StudioRole.ADMIN
    if member_role:
        try:
            return StudioRole(member_role)
        except ValueError:
            pass
    return StudioRole.VIEWER
