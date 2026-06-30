# Audit Remediation — Critical & High Priority

Implemented: project-scoped RBAC at API gate, encryption key separation, gateway session fix, error boundaries, lazy routes, storage deduplication.

## Rollback

1. Revert git commit(s) for this change set.
2. Studio API routers: restore `get_current_admin` imports (admin-only gate).
3. Frontend: restore eager imports in `AdminApp.jsx`; remove `lazyPages.js`.
4. `ENCRYPTION_KEY` unset → encryption continues using `SECRET_KEY` (no data migration needed).

## Verification

```bash
# Backend
cd backend && python -c "from app.main import app; from app.core.deps import require_studio_permission; print('ok')"

# Frontend
npm run build
```

- Studio user with `studio_role` can log in and access project workspaces.
- Platform admin routes (`/studio/platform/admin`, `/api-gateway`, security admin) still require `is_admin`.
- `/metrics` and `/health` unchanged.
