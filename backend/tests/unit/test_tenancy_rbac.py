"""Unit tests for organization-level RBAC."""

import pytest

from app.domain.tenancy.enums import OrganizationRole
from app.domain.tenancy.rbac import org_role_has_permission


@pytest.mark.unit
def test_owner_has_all_org_permissions():
    assert org_role_has_permission(OrganizationRole.OWNER, "org.update")
    assert org_role_has_permission(OrganizationRole.OWNER, "org.billing")
    assert org_role_has_permission(OrganizationRole.OWNER, "branding.manage")


@pytest.mark.unit
def test_guest_read_only():
    assert org_role_has_permission(OrganizationRole.GUEST, "org.read")
    assert not org_role_has_permission(OrganizationRole.GUEST, "org.update")
    assert not org_role_has_permission(OrganizationRole.GUEST, "project.create")


@pytest.mark.unit
def test_billing_admin():
    assert org_role_has_permission(OrganizationRole.BILLING_ADMIN, "org.billing")
    assert org_role_has_permission(OrganizationRole.BILLING_ADMIN, "audit.read")
    assert not org_role_has_permission(OrganizationRole.BILLING_ADMIN, "org.members.manage")
