# UNTOLD Backend API

Production-ready FastAPI backend for the UNTOLD OTT platform.

## Tech Stack

- **FastAPI** — async REST API framework
- **PostgreSQL** — primary database
- **SQLAlchemy 2.0** — ORM with connection pooling
- **JWT** — secure authentication (access + refresh tokens)
- **Alembic** — database migrations
- **Docker** — containerized deployment

## Architecture

```
backend/
├── app/
│   ├── main.py              # FastAPI app, middleware, error handlers
│   ├── core/                # Config, security, dependencies, exceptions
│   ├── db/                  # Engine, sessions, seed data
│   ├── models/              # SQLAlchemy ORM models
│   ├── schemas/             # Pydantic request/response models
│   ├── services/            # Business logic layer
│   └── api/v1/              # REST route handlers
├── alembic/                 # Database migrations
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## Quick Start

### With Docker (recommended)

```bash
cd backend
cp .env.example .env
# Generate a production-grade secret:
# openssl rand -hex 32  →  set SECRET_KEY in .env
docker compose up --build
```

API: http://localhost:8000  
Docs: http://localhost:8000/docs

Docker Compose starts **PostgreSQL**, **Redis**, and the API. Migrations run automatically on startup via `scripts/entrypoint.sh`.

### Local Development

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
cp .env.example .env

# Start PostgreSQL + Redis (or use docker compose up db redis -d)
docker compose up db redis -d

python scripts/validate_env.py   # verify configuration
python run.py
```

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/v1/register` | — | Register new user |
| `POST` | `/api/v1/login` | — | Login, returns JWT |
| `POST` | `/api/v1/auth/refresh` | — | Refresh access token |
| `GET` | `/api/v1/videos` | — | List videos (paginated) |
| `GET` | `/api/v1/video/{id}` | — | Get video by ID |
| `GET` | `/api/v1/videos/{id}` | — | Get video by ID (alias) |
| `POST` | `/api/v1/watchlist` | JWT | Add to watchlist |
| `GET` | `/api/v1/watchlist` | JWT | Get user watchlist |
| `GET` | `/api/v1/analytics` | Admin | Analytics summary |
| `GET` | `/api/v1/categories` | — | List categories |
| `GET` | `/api/v1/admin/dashboard` | Admin | Admin dashboard |

Full interactive docs at `/docs`.

## Database Tables

| Table | Description |
|-------|-------------|
| `users` | User accounts with roles |
| `videos` | Documentaries and shorts |
| `categories` | Content categories |
| `watchlist` | User saved videos |
| `subscriptions` | User subscription plans |
| `analytics` | Event tracking |

## Authentication

```bash
# Register
curl -X POST http://localhost:8000/api/v1/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"securepass123","full_name":"John Doe"}'

# Login
curl -X POST http://localhost:8000/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"securepass123"}'

# Authenticated request
curl http://localhost:8000/api/v1/watchlist \
  -H "Authorization: Bearer <access_token>"
```

## Default Admin (development seed only)

Admin seeding runs only when `SEED_DATABASE=true`. Set a strong `ADMIN_PASSWORD` in `.env` — there is **no default password**.

- Email: `ADMIN_EMAIL` (default `admin@untold.com`)
- Password: value of `ADMIN_PASSWORD` in `.env`

In production, leave `SEED_DATABASE=false` and create admins via a secure bootstrap process.

## Migrations

Schema is managed by **Alembic** (no `create_all()` on startup).

```bash
# Apply all migrations
alembic upgrade head

# Create a new migration after model changes
alembic revision --autogenerate -m "description"
```

Migrations also run automatically on API startup and in the Docker/Railway entrypoint.

**Existing databases** created with the old `create_all()` approach: stamp the current revision without re-creating tables:

```bash
alembic stamp head
```

## Environment Variables

See `.env.example` for all configuration options.

Validate before deploy:

```bash
python scripts/validate_env.py
```

### Production requirements

| Variable | Requirement |
|----------|-------------|
| `SECRET_KEY` | Min 32 chars, `openssl rand -hex 32` |
| `ENVIRONMENT` | `production` |
| `DEBUG` | `false` |
| `REDIS_URL` | Required for rate limiting |
| `SEED_DATABASE` | `false` (recommended) |
| `ADMIN_PASSWORD` | Required only if `SEED_DATABASE=true` |

## Security

- Bcrypt password hashing
- JWT access tokens (30 min) + refresh tokens (7 days)
- Role-based access control (user / admin)
- Redis-backed rate limiting (auth endpoints: 10/min, default: 120/min)
- CORS configuration
- Production environment validation (secret key, debug flag, CORS)
- Global error handling (no stack traces in production)
- SQL injection protection via ORM parameterized queries
