"""Tenant scoping helpers for AI generation queries."""

from __future__ import annotations

from sqlalchemy import and_, or_
from sqlalchemy.orm import Query, Session

from app.domain.tenancy.context import TenantContextService
from app.models import User
from app.models.studio.ai import AIGeneration
from app.models.studio.core import Production


def user_organization_ids(db: Session, user: User) -> list[int]:
    from app.models.studio.tenancy import OrganizationMember

    rows = db.query(OrganizationMember.organization_id).filter(OrganizationMember.user_id == user.id).all()
    return [row[0] for row in rows]


def scope_ai_generations_query(db: Session, user: User, query: Query) -> Query:
    """Restrict AI generation rows to the caller's tenant context."""
    if user.is_admin:
        return query

    org_ids = user_organization_ids(db, user)
    own_jobs = and_(AIGeneration.organization_id.is_(None), AIGeneration.created_by_id == user.id)
    if not org_ids:
        return query.filter(own_jobs)

    org_jobs = AIGeneration.organization_id.in_(org_ids)
    project_jobs = AIGeneration.project_id.in_(
        db.query(Production.id).filter(Production.organization_id.in_(org_ids))
    )
    return query.filter(or_(org_jobs, project_jobs, own_jobs))


def resolve_generation_organization_id(
    db: Session,
    user: User,
    project_id: int | None,
) -> int | None:
    if project_id:
        production = db.query(Production).filter(Production.id == project_id).first()
        if production and production.organization_id:
            return production.organization_id
    return TenantContextService.resolve_primary_org_id(db, user.id)
