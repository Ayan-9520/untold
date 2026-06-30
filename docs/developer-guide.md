# Developer Guide

Guide for engineers contributing to the UNTOLD monorepo.

## Prerequisites

| Tool | Version |
|------|---------|
| Node.js | 20+ |
| Python | 3.11+ |
| Docker | 24+ (recommended) |
| PostgreSQL | 16 (or use Docker) |
| Redis | 7 (or use Docker) |

## Quick start

### Option A — Full stack (Docker)

```bash
cp deploy/env/development.env.example .env
docker compose up -d --build
```

| Service | URL |
|---------|-----|
| Web | http://localhost:8080 |
| API | http://localhost:8000 |
| API docs | http://localhost:8000/docs |

### Option B — Local frontend + Docker backend

```bash
# Terminal 1 — backend
docker compose up -d postgres redis api celery_worker celery_beat

# Terminal 2 — frontend
cp .env.example .env
npm install
npm run dev
```

| Surface | URL |
|---------|-----|
| Website | http://localhost:5173 |
| Mobile | http://localhost:5173/app |
| Studio | http://localhost:5173/studio |
| AI | http://localhost:5173/ai |

### Option C — Backend only (local Python)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

## Default credentials

| Role | Email | Password |
|------|-------|----------|
| Admin / Studio | `admin@untold.com` | `ChangeMe123!` |
| Consumer | `alex@untold.com` | `Untold123!` |

## Project conventions

### Backend (Python)

```
backend/app/
├── api/v1/       # HTTP routes — thin, delegate to services
├── services/     # Orchestration
├── domain/       # Business logic, RBAC, provider registries
├── ai/           # Unified AI layer
├── models/       # SQLAlchemy ORM
├── schemas/      # Pydantic request/response
├── workers/      # Celery tasks
└── core/         # Config, deps, security
```

**Rules:**

- Add routes in `api/v1/<module>.py`, register in `router.py`
- Business logic in `domain/` or `services/`, not in route handlers
- New tables: model + Alembic migration
- Use `AppException` subclasses for domain errors
- Type hints on all public functions

### Frontend (React)

```
src/
├── pages/           # Consumer pages
├── admin/           # UNTOLD Studio (/studio)
├── ai/              # UNTOLD AI product (/ai)
├── app/             # Mobile OTT (/app)
├── components/      # Shared UI
├── api/             # Axios clients
└── data/            # Mock catalogs (dev)
```

**Rules:**

- Studio features in `src/admin/features/<name>/`
- Lazy-load studio pages via `src/admin/routes/lazyPages.js`
- Use TanStack Query for server state in studio
- Sanitize HTML before `dangerouslySetInnerHTML` (`src/utils/sanitizeHtml.js`)
- Match existing Tailwind patterns — no new CSS frameworks

### Git workflow

1. Branch from `develop` or `main`
2. Run tests locally before PR
3. CI must pass (lint, pytest, vitest, build)
4. Production releases: tag `v*.*.*`

## Environment variables

| File | Purpose |
|------|---------|
| `.env` (root) | `VITE_API_URL` for frontend |
| `backend/.env` | API secrets, DB URL |
| `deploy/env/*.env.example` | Environment templates |

Key backend variables: `DATABASE_URL`, `SECRET_KEY`, `REDIS_URL`, `CORS_ORIGINS`.

## Database

```bash
cd backend
alembic upgrade head          # apply migrations
alembic revision -m "message" # create migration
```

See [Database](./database.md).

## Testing

```bash
# Backend
cd backend
pip install -r requirements-dev.txt
pytest
pytest --cov=app --cov-report=term-missing

# Frontend unit
npm test
npm run test:coverage

# E2E
npm run test:e2e
```

See [Testing Guide](./testing-guide.md).

## Linting

```bash
npm run lint          # oxlint (frontend)
# Backend: ruff/flake8 per CI config
```

## API development

1. Define Pydantic schema in `app/schemas/`
2. Add service method in `app/services/` or `app/domain/`
3. Add route in `app/api/v1/`
4. Register router in `app/api/v1/router.py`
5. Add integration test in `backend/tests/`

Interactive docs: http://localhost:8000/docs

## AI provider development

1. Implement provider in `app/ai/providers/` or domain bridge
2. Register in `app/ai/bootstrap.py` only
3. Verify: `python -c "from app.ai import ensure_bootstrapped; ensure_bootstrapped()"`

See [AI](./ai.md).

## Studio feature development

1. Add API endpoints (with RBAC dependencies)
2. Create feature folder: `src/admin/features/<feature>/`
3. Add page in `src/admin/pages/`
4. Register route in `AdminApp.jsx` and `lazyPages.js`
5. Add nav item in `src/admin/config/studioNav.js`

## Debugging

| Issue | Check |
|-------|-------|
| CORS errors | `CORS_ORIGINS` includes frontend origin |
| 401 on studio | Token in localStorage; `studio_role` assigned |
| DB connection | `DATABASE_URL`, postgres container health |
| Redis errors | `REDIS_URL`, redis container |
| AI stub responses | Provider API keys in `.env` |

API logs: `docker compose logs -f api`  
Structured JSON in production: `LOG_FORMAT=json`

## Useful commands

```bash
docker compose ps
docker compose logs -f api celery_worker
docker compose exec api alembic current
docker compose exec postgres psql -U untold -d untold_db
celery -A app.workers.celery_app inspect ping
```

## Related documents

- [Folder Structure](./folder-structure.md)
- [Architecture](./architecture.md)
- [API](./api.md)
- [Authentication](./authentication.md)
- [Testing Guide](./testing-guide.md)
