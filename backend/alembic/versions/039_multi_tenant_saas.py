"""Multi-tenant SaaS migration — organizations, workspaces, RLS, backfill."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "039_multi_tenant_saas"
down_revision: Union[str, None] = "038_ai_prompt_versioning"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _pg_enum(name: str, *values: str) -> postgresql.ENUM:
    enum_type = postgresql.ENUM(*values, name=name)
    enum_type.create(op.get_bind(), checkfirst=True)
    return postgresql.ENUM(*values, name=name, create_type=False)


def upgrade() -> None:
    org_status = _pg_enum("organizationstatus", "active", "trial", "suspended", "cancelled")
    org_plan = _pg_enum("organizationplan", "free", "starter", "pro", "enterprise")
    org_role = _pg_enum("organizationrole", "owner", "admin", "billing_admin", "member", "guest")
    team_role = _pg_enum("teamrole", "lead", "member")
    workspace_role = _pg_enum("workspacerole", "admin", "editor", "viewer")
    invite_status = _pg_enum("invitationstatus", "pending", "accepted", "revoked", "expired")

    op.create_table(
        "organizations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("status", org_status, server_default="active", nullable=False),
        sa.Column("plan", org_plan, server_default="free", nullable=False),
        sa.Column("seat_limit", sa.Integer(), server_default="3", nullable=False),
        sa.Column("seats_used", sa.Integer(), server_default="0", nullable=False),
        sa.Column("storage_quota_bytes", sa.BigInteger(), server_default="5368709120", nullable=False),
        sa.Column("storage_used_bytes", sa.BigInteger(), server_default="0", nullable=False),
        sa.Column("api_rate_limit_tier", sa.String(length=32), server_default="standard", nullable=False),
        sa.Column("billing_customer_id", sa.String(length=255), nullable=True),
        sa.Column("billing_subscription_id", sa.String(length=255), nullable=True),
        sa.Column("settings", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
        sa.Column("branding", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
        sa.Column("white_label", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
        sa.Column("usage_limits", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
        sa.Column("usage_counters", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
        sa.Column("is_system_default", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_organizations_slug", "organizations", ["slug"], unique=True)
    op.create_index("ix_organizations_status", "organizations", ["status"])
    op.create_index("ix_organizations_plan", "organizations", ["plan"])

    op.create_table(
        "organization_members",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("role", org_role, server_default="member", nullable=False),
        sa.Column("is_primary", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("joined_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "user_id", name="uq_org_member"),
    )
    op.create_index("ix_organization_members_org", "organization_members", ["organization_id"])
    op.create_index("ix_organization_members_user", "organization_members", ["user_id"])

    op.create_table(
        "teams",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "slug", name="uq_team_org_slug"),
    )

    op.create_table(
        "team_members",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("team_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("role", team_role, server_default="member", nullable=False),
        sa.Column("joined_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("team_id", "user_id", name="uq_team_member"),
    )

    op.create_table(
        "workspaces",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("team_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("settings", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
        sa.Column("is_default", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "slug", name="uq_workspace_org_slug"),
    )

    op.create_table(
        "workspace_members",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("workspace_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("role", workspace_role, server_default="editor", nullable=False),
        sa.Column("joined_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("workspace_id", "user_id", name="uq_workspace_member"),
    )

    op.create_table(
        "organization_invitations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("role", org_role, server_default="member", nullable=False),
        sa.Column("token_hash", sa.String(length=128), nullable=False),
        sa.Column("status", invite_status, server_default="pending", nullable=False),
        sa.Column("workspace_ids", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("invited_by_id", sa.Integer(), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["invited_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_index("ix_org_invitations_email", "organization_invitations", ["email"])
    op.create_index("ix_org_invitations_status", "organization_invitations", ["status"])

    op.create_table(
        "organization_billing_accounts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("plan_catalog_id", sa.Integer(), nullable=True),
        sa.Column("external_customer_id", sa.String(length=255), nullable=True),
        sa.Column("external_subscription_id", sa.String(length=255), nullable=True),
        sa.Column("currency", sa.String(length=10), server_default="usd", nullable=False),
        sa.Column("billing_email", sa.String(length=255), nullable=True),
        sa.Column("meta", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id"),
    )

    op.create_table(
        "tenant_audit_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(length=120), nullable=False),
        sa.Column("resource_type", sa.String(length=64), nullable=True),
        sa.Column("resource_id", sa.String(length=64), nullable=True),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("meta", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("checksum", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_tenant_audit_org", "tenant_audit_events", ["organization_id"])
    op.create_index("ix_tenant_audit_action", "tenant_audit_events", ["action"])
    op.create_index("ix_tenant_audit_created", "tenant_audit_events", ["created_at"])

    # Tenant columns on existing tables (nullable for backward compatibility during rollout)
    op.add_column("productions", sa.Column("organization_id", sa.Integer(), nullable=True))
    op.add_column("productions", sa.Column("workspace_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_productions_organization_id", "productions", "organizations", ["organization_id"], ["id"], ondelete="CASCADE"
    )
    op.create_foreign_key(
        "fk_productions_workspace_id", "productions", "workspaces", ["workspace_id"], ["id"], ondelete="SET NULL"
    )
    op.create_index("ix_productions_organization_id", "productions", ["organization_id"])
    op.create_index("ix_productions_workspace_id", "productions", ["workspace_id"])

    op.add_column("studio_api_keys", sa.Column("organization_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_studio_api_keys_organization_id",
        "studio_api_keys",
        "organizations",
        ["organization_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index("ix_studio_api_keys_organization_id", "studio_api_keys", ["organization_id"])

    # Backfill default organization for existing data
    op.execute(
        """
        INSERT INTO organizations (slug, name, status, plan, is_system_default, settings, branding, white_label, usage_limits, usage_counters)
        VALUES ('untold-default', 'UNTOLD Default', 'active', 'pro', true, '{}', '{}', '{}', '{}', '{}')
        ON CONFLICT (slug) DO NOTHING
        """
    )
    op.execute(
        """
        INSERT INTO workspaces (organization_id, name, slug, description, is_default, settings)
        SELECT o.id, 'Default Workspace', 'default', 'Migrated default workspace', true, '{}'
        FROM organizations o WHERE o.slug = 'untold-default'
        AND NOT EXISTS (
            SELECT 1 FROM workspaces w WHERE w.organization_id = o.id AND w.slug = 'default'
        )
        """
    )
    op.execute(
        """
        UPDATE productions p
        SET organization_id = o.id,
            workspace_id = w.id
        FROM organizations o
        JOIN workspaces w ON w.organization_id = o.id AND w.is_default = true
        WHERE o.slug = 'untold-default' AND p.organization_id IS NULL
        """
    )
    op.execute(
        """
        INSERT INTO organization_members (organization_id, user_id, role, is_primary)
        SELECT o.id, u.id,
            CASE WHEN u.is_admin THEN 'owner'::organizationrole ELSE 'member'::organizationrole END,
            true
        FROM users u
        CROSS JOIN organizations o
        WHERE o.slug = 'untold-default'
          AND (u.studio_role IS NOT NULL OR u.is_admin = true)
          AND NOT EXISTS (
            SELECT 1 FROM organization_members m
            WHERE m.organization_id = o.id AND m.user_id = u.id
          )
        """
    )
    op.execute(
        """
        UPDATE organizations o
        SET seats_used = (
            SELECT COUNT(*) FROM organization_members m WHERE m.organization_id = o.id
        )
        WHERE o.slug = 'untold-default'
        """
    )

    # Row-level security (PostgreSQL)
    op.execute("ALTER TABLE productions ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE tenant_audit_events ENABLE ROW LEVEL SECURITY")
    op.execute(
        """
        CREATE POLICY productions_tenant_select ON productions FOR SELECT
        USING (
            current_setting('app.bypass_rls', true) = 'true'
            OR organization_id IS NULL
            OR organization_id = NULLIF(current_setting('app.current_organization_id', true), '')::integer
        )
        """
    )
    op.execute(
        """
        CREATE POLICY productions_tenant_modify ON productions FOR ALL
        USING (
            current_setting('app.bypass_rls', true) = 'true'
            OR organization_id IS NULL
            OR organization_id = NULLIF(current_setting('app.current_organization_id', true), '')::integer
        )
        WITH CHECK (
            current_setting('app.bypass_rls', true) = 'true'
            OR organization_id IS NULL
            OR organization_id = NULLIF(current_setting('app.current_organization_id', true), '')::integer
        )
        """
    )
    op.execute(
        """
        CREATE POLICY tenant_audit_org_isolation ON tenant_audit_events FOR ALL
        USING (
            current_setting('app.bypass_rls', true) = 'true'
            OR organization_id = NULLIF(current_setting('app.current_organization_id', true), '')::integer
        )
        WITH CHECK (
            current_setting('app.bypass_rls', true) = 'true'
            OR organization_id = NULLIF(current_setting('app.current_organization_id', true), '')::integer
        )
        """
    )


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS tenant_audit_org_isolation ON tenant_audit_events")
    op.execute("DROP POLICY IF EXISTS productions_tenant_modify ON productions")
    op.execute("DROP POLICY IF EXISTS productions_tenant_select ON productions")
    op.execute("ALTER TABLE tenant_audit_events DISABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE productions DISABLE ROW LEVEL SECURITY")

    op.drop_constraint("fk_studio_api_keys_organization_id", "studio_api_keys", type_="foreignkey")
    op.drop_index("ix_studio_api_keys_organization_id", table_name="studio_api_keys")
    op.drop_column("studio_api_keys", "organization_id")

    op.drop_constraint("fk_productions_workspace_id", "productions", type_="foreignkey")
    op.drop_constraint("fk_productions_organization_id", "productions", type_="foreignkey")
    op.drop_index("ix_productions_workspace_id", table_name="productions")
    op.drop_index("ix_productions_organization_id", table_name="productions")
    op.drop_column("productions", "workspace_id")
    op.drop_column("productions", "organization_id")

    op.drop_table("tenant_audit_events")
    op.drop_table("organization_billing_accounts")
    op.drop_table("organization_invitations")
    op.drop_table("workspace_members")
    op.drop_table("workspaces")
    op.drop_table("team_members")
    op.drop_table("teams")
    op.drop_table("organization_members")
    op.drop_table("organizations")

    for name in (
        "invitationstatus",
        "workspacerole",
        "teamrole",
        "organizationrole",
        "organizationplan",
        "organizationstatus",
    ):
        sa.Enum(name=name).drop(op.get_bind(), checkfirst=True)
