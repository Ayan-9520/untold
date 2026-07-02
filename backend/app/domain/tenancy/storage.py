"""Tenant-isolated storage key prefixes."""


def tenant_storage_prefix(organization_id: int, workspace_id: int | None = None) -> str:
    """S3/R2 key prefix — enforces storage isolation per organization."""
    base = f"orgs/{organization_id}"
    if workspace_id is not None:
        return f"{base}/workspaces/{workspace_id}"
    return base


def tenant_asset_key(organization_id: int, workspace_id: int, project_id: int, filename: str) -> str:
    return f"{tenant_storage_prefix(organization_id, workspace_id)}/projects/{project_id}/{filename}"
