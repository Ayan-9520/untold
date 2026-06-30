# Runbook: Database Migration

## Pre-migration checklist

- [ ] Migration tested locally: `alembic upgrade head`
- [ ] Downgrade tested for risky changes
- [ ] Backup taken (see [Backup & Restore](./backup-restore.md))
- [ ] Migration is backward-compatible OR deploy plan coordinates API + DB
- [ ] Large table changes use batching / `CONCURRENTLY` indexes

## Apply migration

### Docker / K8s (production pattern)

Set on API deployment only:

```yaml
env:
  - name: RUN_MIGRATIONS
    value: "true"
```

Entrypoint runs `alembic upgrade head` once on startup.

### Manual

```bash
cd backend
alembic current
alembic upgrade head
alembic current
```

### Kubernetes one-off job

```bash
kubectl run alembic-migrate -n untold \
  --image=ghcr.io/org/untold-api:latest \
  --restart=Never \
  --env="RUN_MIGRATIONS=true" \
  --command -- alembic upgrade head
```

## Zero-downtime patterns

### Additive changes (safe)

1. Deploy migration (add nullable column)
2. Deploy API code that writes new column
3. Backfill data
4. Deploy migration (add NOT NULL constraint)

### Destructive changes (careful)

1. Deploy code that stops reading old column
2. Deploy migration to drop column
3. Never drop before code no longer references

### pgvector / extensions

Migration `027` enables extension — requires superuser on first run. Managed providers often pre-enable `vector`.

## Failed migration

### Symptoms

- API pods CrashLoop on startup
- `alembic upgrade` errors in logs

### Recovery

1. Check `alembic current` vs expected
2. Fix migration file if bug (new revision, not edit applied)
3. Manual SQL fix if partially applied:

```sql
-- Example: mark version if manually fixed
-- Only if alembic_version out of sync
UPDATE alembic_version SET version_num = '038_ai_prompt_versioning';
```

4. Restore from backup if data corrupted

## Create new migration

```bash
cd backend
alembic revision -m "add_feature_x"
# Edit alembic/versions/XXX_add_feature_x.py
alembic upgrade head
pytest tests/integration/
```

## Long-running migrations

For tables > 1M rows:

- Use `op.execute("CREATE INDEX CONCURRENTLY ...")` outside transaction
- Schedule during maintenance window
- Monitor replication lag on read replicas

## Related

- [Database](../database.md)
- [Backup & Restore](./backup-restore.md)
