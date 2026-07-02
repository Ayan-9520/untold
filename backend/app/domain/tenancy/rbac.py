"""Organization-level RBAC — separate from project-scoped StudioRole."""

from __future__ import annotations

from app.domain.tenancy.enums import OrganizationRole

ORG_PERMISSIONS: dict[str, frozenset[OrganizationRole]] = {
    "org.read": frozenset(OrganizationRole),
    "org.update": frozenset({OrganizationRole.OWNER, OrganizationRole.ADMIN}),
    "org.delete": frozenset({OrganizationRole.OWNER}),
    "org.billing": frozenset({OrganizationRole.OWNER, OrganizationRole.ADMIN, OrganizationRole.BILLING_ADMIN}),
    "org.invite": frozenset({OrganizationRole.OWNER, OrganizationRole.ADMIN}),
    "org.members.manage": frozenset({OrganizationRole.OWNER, OrganizationRole.ADMIN}),
    "team.manage": frozenset({OrganizationRole.OWNER, OrganizationRole.ADMIN, OrganizationRole.MEMBER}),
    "workspace.manage": frozenset({OrganizationRole.OWNER, OrganizationRole.ADMIN}),
    "workspace.read": frozenset(OrganizationRole),
    "project.create": frozenset({
        OrganizationRole.OWNER,
        OrganizationRole.ADMIN,
        OrganizationRole.MEMBER,
    }),
    "settings.manage": frozenset({OrganizationRole.OWNER, OrganizationRole.ADMIN}),
    "branding.manage": frozenset({OrganizationRole.OWNER, OrganizationRole.ADMIN}),
    "api_keys.manage": frozenset({OrganizationRole.OWNER, OrganizationRole.ADMIN}),
    "audit.read": frozenset({OrganizationRole.OWNER, OrganizationRole.ADMIN, OrganizationRole.BILLING_ADMIN}),
}


def org_role_has_permission(role: OrganizationRole | str, permission: str) -> bool:
    allowed = ORG_PERMISSIONS.get(permission)
    if not allowed:
        return False
    if isinstance(role, str):
        try:
            role = OrganizationRole(role)
        except ValueError:
            return False
    return role in allowed
