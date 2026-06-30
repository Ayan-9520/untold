# Testing Guide

Production-ready test infrastructure for UNTOLD — backend (pytest), frontend (Vitest + RTL), and E2E (Playwright).

## Folder Structure

```
untold/
├── backend/
│   ├── pytest.ini                 # Pytest + coverage config
│   ├── .coveragerc                # Coverage omit rules
│   ├── requirements-dev.txt       # pytest, pytest-cov, httpx, …
│   └── tests/
│       ├── conftest.py            # Env bootstrap, DB + client fixtures
│       ├── factories/
│       │   ├── __init__.py
│       │   └── user.py            # User / studio user / token headers
│       ├── mocks/
│       │   ├── __init__.py
│       │   └── redis.py           # FakeRedis, ping patch
│       ├── unit/
│       │   ├── test_security.py
│       │   ├── test_sanitization.py
│       │   ├── test_rbac.py
│       │   └── test_ai_registry.py
│       └── integration/
│           ├── test_health_api.py
│           └── test_auth_api.py
├── src/
│   ├── test/
│   │   ├── setup.js               # Vitest + jest-dom
│   │   ├── utils/
│   │   │   └── render.jsx         # renderWithRouter helper
│   │   └── mocks/
│   │       └── adminApi.js
│   ├── utils/
│   │   └── sanitizeHtml.test.js
│   └── admin/components/
│       └── ProtectedRoute.test.jsx
├── e2e/
│   └── smoke.spec.js              # Playwright smoke tests
├── playwright.config.js
└── vite.config.js                 # Vitest config (test block)
```

## Quick Start

### Backend

```bash
# Requires PostgreSQL (untold_test) and Redis optional when RATE_LIMIT_ENABLED=false
createdb untold_test   # once

cd backend
pip install -r requirements.txt -r requirements-dev.txt
pytest                    # all tests + coverage report
pytest -m unit            # fast, no DB writes
pytest -m integration     # API tests with PostgreSQL
pytest --cov-fail-under=25
```

### Frontend

```bash
npm install
npm test                  # Vitest single run
npm run test:watch        # watch mode
npm run test:coverage     # with v8 coverage
```

### E2E (Playwright)

```bash
npm run build
npm run test:e2e          # uses preview server on :4173 in CI
npm run test:e2e:ui       # interactive UI mode
```

### Docker stack

```bash
docker compose up -d db redis
cd backend && pytest
```

## Coverage Targets

| Layer    | CI gate (current) | Production target | Config |
|----------|-------------------|-------------------|--------|
| Backend  | **25%**           | **70%**           | `COVERAGE_BACKEND_MIN` in CI; `backend/.coveragerc` |
| Frontend | **5%**            | **60%**           | `vite.config.js` → `test.coverage.thresholds` |

Raise CI gates incrementally as test suites grow. Backend omits seed scripts and workers from coverage.

## Fixtures & Factories

### Backend (`tests/conftest.py`)

| Fixture | Scope | Purpose |
|---------|-------|---------|
| `engine` | session | Alembic migrate + SQLAlchemy engine |
| `db_session` | function | Transaction rolled back per test |
| `client` | function | FastAPI `TestClient` with DB override |
| `auth_headers` | function | Bearer token for regular user |
| `studio_auth_headers` | function | Bearer token for studio producer |

### User factory (`tests/factories/user.py`)

```python
from tests.factories.user import create_user, create_studio_user, user_token_headers

user = create_user(db_session, email="a@b.com", password="TestPass123!")
headers = user_token_headers(user)
```

### Mocks (`tests/mocks/redis.py`)

```python
from tests.mocks.redis import patch_redis_ping

with patch_redis_ping(True):
    ...
```

### Frontend (`src/test/`)

- `renderWithRouter()` — MemoryRouter wrapper
- `src/test/mocks/adminApi.js` — vi.mock template for admin API

## Sample Tests

### Backend unit

```python
@pytest.mark.unit
def test_access_token_contains_issuer_and_type():
    token = create_access_token(42)
    payload = decode_token(token)
    assert payload["iss"] == "untold"
```

### Backend integration

```python
@pytest.mark.integration
def test_register_login_and_me(client):
    client.post("/api/v1/auth/register", json={...})
    login = client.post("/api/v1/auth/login", json={...})
    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {login.json()['access_token']}"})
    assert me.status_code == 200
```

### Frontend (Vitest + RTL)

```javascript
it('redirects unauthenticated users to studio login', () => {
  mockUseAdminAuth.mockReturnValue({ loading: false, isAuthenticated: false, hasStudioAccess: false });
  renderProtected();
  expect(screen.getByText('Login Page')).toBeInTheDocument();
});
```

### Playwright E2E

```javascript
test('home page loads', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveTitle(/UNTOLD/i);
});
```

## CI Changes

`.github/workflows/ci.yml` now runs:

1. **backend** — `pytest --cov-fail-under=25` with Postgres + Redis services
2. **frontend** — `npm run lint`, `npm run test:coverage`, `npm run build`
3. **e2e** — Playwright smoke tests on production build
4. **docker** — image builds after all tests pass

Coverage artifacts uploaded on every run (`backend/coverage.xml`, `coverage/lcov.info`).

## Markers

```bash
pytest -m unit          # no database required
pytest -m integration   # PostgreSQL required
pytest -m "not slow"
```

## Writing New Tests

1. **Pure logic** → `backend/tests/unit/`, mark `@pytest.mark.unit`
2. **API routes** → `backend/tests/integration/`, use `client` + factories
3. **React components** → colocate `*.test.jsx` or under `src/**/__tests__/`
4. **User flows** → `e2e/*.spec.js`

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `untold_test` DB missing | `createdb untold_test` or use Docker Postgres |
| Settings cached | `get_settings.cache_clear()` (handled in conftest) |
| Rate limit 429 in tests | Set `RATE_LIMIT_ENABLED=false` (conftest default) |
| Playwright can't reach app | Run `npm run build` first; CI builds automatically |
| Coverage gate fails | Add tests or adjust `COVERAGE_*_MIN` temporarily while ramping |

## Production Checklist

- [ ] CI green on PR (backend + frontend + e2e + docker)
- [ ] Coverage trending toward 70% / 60% targets
- [ ] Integration tests run against migrated schema (`alembic upgrade head`)
- [ ] E2E smoke covers critical routes (home, studio login)
- [ ] No secrets in test fixtures (use `test-secret-key-...` only)
