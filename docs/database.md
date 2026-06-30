# Database

UNTOLD uses **PostgreSQL 16** as the system of record. Schema is managed with **Alembic** migrations; ORM models live in `backend/app/models/`.

## Schema overview

```mermaid
erDiagram
  users ||--o{ watchlist : has
  users ||--o{ subscriptions : has
  users ||--o{ analytics : generates
  videos ||--o{ watchlist : saved_in
  videos }o--|| categories : belongs_to
  users ||--o{ studio_project_members : joins
  studio_projects ||--o{ studio_tasks : contains
  studio_projects ||--o{ research_sessions : has
  studio_projects ||--o{ scripts : has
  studio_projects ||--o{ storyboard_scenes : has
  ai_prompt_library ||--o{ ai_generations : templates
```

## Domain groups

### Core platform (`001_initial_schema`)

| Table | Purpose |
|-------|---------|
| `users` | Accounts, `studio_role`, MFA flags |
| `admin_users` | Admin metadata linked to users |
| `categories` | Video taxonomy |
| `videos` | OTT catalog (documentaries, shorts, series) |
| `watchlist` | User saved content |
| `subscriptions` | Plan enrollment |
| `analytics` | Event tracking |
| `localization_jobs` | AI localization pipeline |

### Engagement & monetization

| Migration range | Tables |
|-----------------|--------|
| `002`–`004` | News engine, live engine, monetization |
| `news_*` | Articles, sources, tags, categories |
| `live_*` | Matches, events, commentary, fixtures |
| `payments`, `invoices`, `plan_catalog` | Billing |
| `watch_history`, `video_progress` | Playback state |
| `magazine_editions` | E-magazine |

### Studio platform (`005`–`016`)

| Area | Key tables |
|------|------------|
| Productions | `productions`, `ai_agent_jobs` |
| Platform | `studio_projects`, `studio_project_members`, `studio_tasks` |
| Auth & admin | `studio_api_keys`, `studio_security_logs`, `studio_feature_flags` |
| Calendar | `calendar_events`, `studio_approvals`, `studio_notifications` |

### Creative workspaces (`009`–`026`)

| Studio | Tables |
|--------|--------|
| Research | `research_sessions`, `research_sources`, `research_notes`, `research_ai_interactions` |
| Script | `scripts`, `script_versions`, `script_ai_interactions` |
| Storyboard | `storyboard_scenes`, `storyboard_revisions` |
| Assets | `studio_assets`, `asset_versions`, `asset_collections` |
| Timeline | `timeline_sessions`, `timeline_snapshots`, `timeline_export_jobs` |
| Publishing | `publish_jobs`, `publish_webhooks`, `publish_agent_runs` |
| AI studios | `ai_generations`, `ai_image_versions`, `ai_video_versions`, `ai_voice_versions`, `ai_music_versions`, `ai_shorts_versions`, `ai_seo_variants`, `ai_translation_versions` |
| Prompts | `ai_prompt_library` (versioned: `prompt_key`, `version`, `is_current`) |

### Platform services (`027`–`038`)

| Migration | Feature |
|-----------|---------|
| `027` | pgvector extension, embedding storage |
| `028`–`031` | Production pipeline, workflow engine |
| `032` | Agent marketplace |
| `033` | AI cost optimization (`ai_cost_budgets`, `ai_response_cache`) |
| `034` | Enterprise collaboration |
| `035` | Plugin SDK |
| `036` | API gateway usage logs |
| `037` | Enterprise security (IdP, MFA, sessions, audit) |
| `038` | AI prompt versioning columns |

Full migration list: `backend/alembic/versions/`.

## Entity relationship (studio project)

```mermaid
flowchart TB
  SP[studio_projects]
  SP --> Members[studio_project_members]
  SP --> Tasks[studio_tasks]
  SP --> Research[research_sessions]
  SP --> Scripts[scripts]
  SP --> Storyboard[storyboard_scenes]
  SP --> Assets[studio_assets]
  SP --> Timeline[timeline_sessions]
  SP --> Publish[publish_jobs]
  SP --> Workflow[workflow_runs]
  Members --> Users[users]
```

## Conventions

### Naming

- Tables: `snake_case`, plural (`studio_projects`)
- Foreign keys: `{table_singular}_id` (`project_id`)
- Enums: PostgreSQL native enums via Alembic `_pg_enum()` helper
- JSON payloads: `*_json` text columns (serialized JSON strings)

### ORM

- SQLAlchemy 2.0 style: `Mapped[]`, `mapped_column`
- Base class: `app.db.base.Base`
- String enums: `StrEnum` wrapper for cross-DB compatibility in tests
- Relationships: explicit `back_populates`, cascade rules on owned children

### Timestamps

Most tables include:

- `created_at` — `server_default=now()`
- `updated_at` — `onupdate=now()` where mutable

### Soft delete

Not global — use `is_active` flags on content tables (`videos.is_active`) rather than row deletion for catalog items.

## Migrations

### Apply

```bash
cd backend
alembic upgrade head
```

Docker entrypoint runs migrations when `RUN_MIGRATIONS=true` (production deploy).

### Create

```bash
cd backend
alembic revision -m "describe_change"
# Edit the generated file in alembic/versions/
alembic upgrade head
```

### Rules

1. **Never edit applied migrations** in shared environments — add a new revision.
2. **Backfill in migrations** only for small, idempotent data fixes.
3. **Test downgrade** for risky schema changes before production.
4. **pgvector** — ensure extension enabled (`027_vector_store_pgvector.py`).

## Connection configuration

| Variable | Example |
|----------|---------|
| `DATABASE_URL` | `postgresql://user:pass@host:5432/untold_db` |

Pool settings are configured in `app/db/session.py`. Use connection pooling (PgBouncer) in high-traffic production.

## Indexing strategy

- Primary keys and foreign keys indexed by default
- Unique constraints on `email`, `slug` fields
- Composite unique: `watchlist (user_id, video_id)`
- Time-series queries: `analytics.created_at`, `ai_generations.created_at`

Review `EXPLAIN ANALYZE` for slow studio list endpoints before adding indexes.

## Seeding

Development seed (`app/db/init_db.py`) runs when `SEED_DATABASE=true` or on local startup (non-Docker).

**Production:** `SEED_DATABASE=false` always.

Default dev credentials are documented in the [Developer Guide](./developer-guide.md).

## Backup & restore

- Daily logical backups via `deploy/scripts/backup.sh` or K8s CronJob
- Restore: `deploy/scripts/restore.sh`
- See [Runbooks: Backup & Restore](./runbooks/backup-restore.md)

## Test database

Pytest uses SQLite or ephemeral PostgreSQL per `backend/tests/conftest.py`. Enum and JSON behavior may differ — run integration tests against Postgres in CI.

## Related documents

- [Architecture](./architecture.md)
- [Runbooks: Database Migration](./runbooks/database-migration.md)
- [AI](./ai.md) — `ai_prompt_library` versioning
