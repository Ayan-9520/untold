"""Tenant context dependencies — organization and workspace resolution."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.core.deps import get_current_studio_user
from app.db.session import get_db
from app.domain.tenancy.context import TenantContext, TenantContextService
from app.models import User


def get_organization_id_header(
    x_organization_id: Annotated[int | None, Header(alias="X-Organization-ID")] = None,
) -> int | None:
    return x_organization_id


def get_workspace_id_header(
    x_workspace_id: Annotated[int | None, Header(alias="X-Workspace-ID")] = None,
) -> int | None:
    return x_workspace_id


def get_tenant_context(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
    organization_id: int | None = Depends(get_organization_id_header),
    workspace_id: int | None = Depends(get_workspace_id_header),
) -> TenantContext:
    resolved_org_id = TenantContextService.resolve_organization_id(db, user, organization_id)
    ctx = TenantContextService.build_context(
        db, user, organization_id=resolved_org_id, workspace_id=workspace_id
    )
    TenantContextService.apply_rls(db, ctx.organization_id, bypass=user.is_admin)
    return ctx


def require_org_permission(permission: str):
    def _checker(ctx: TenantContext = Depends(get_tenant_context)) -> TenantContext:
        TenantContextService.require_org_permission(ctx, permission)
        return ctx

    return _checker
