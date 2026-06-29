# UNTOLD — Full-Stack Ecosystem

Global Sports Storytelling Media Platform · OTT · Digital Media

**The Story Behind The Glory**

---

## Architecture

```
untold/
├── src/                    # React frontend (Website + Mobile App + Admin)
│   ├── pages/              # Website: Home, About, Originals, Legends, Rivalries, Shorts, Contact
│   ├── app/                # Mobile OTT UI (/app)
│   ├── admin/              # Admin dashboard (/admin)
│   ├── api/                # Axios clients → FastAPI
│   └── components/brand/   # Logo (full website / compact app)
├── backend/                # FastAPI + PostgreSQL
│   ├── app/models/         # users, videos, categories, watchlist, subscriptions, analytics, admin_users
│   ├── app/api/v1/         # REST endpoints
│   └── app/db/             # Seed: 20 users, 50 videos, 4 categories
├── vercel.json             # Frontend deployment
└── backend/railway.toml      # Backend deployment
```

---

## Quick Start (Local)

### 1. Backend + Database

```bash
cd backend
cp .env.example .env
docker compose up --build
```

API: http://localhost:8000/docs

### 2. Frontend

```bash
cp .env.example .env
npm install
npm run dev
```

| Surface | URL |
|---------|-----|
| Website | http://localhost:5173 |
| Mobile App | http://localhost:5173/app |
| Admin | http://localhost:5173/admin |

**Admin login:** `admin@untold.com` / `ChangeMe123!`  
**Test user:** `alex@untold.com` / `Untold123!`

---

## Brand Logos

| Context | Variant | Usage |
|---------|---------|-------|
| Website hero | `Logo variant="full"` | Full wordmark + tagline + gold slash |
| Website nav | `Logo variant="horizontal"` | Compact horizontal wordmark |
| Mobile app | `Logo variant="compact"` | Stacked UN/TOLD in gold border style |

---

## API Endpoints

| Method | Endpoint | Auth |
|--------|----------|------|
| POST | `/api/v1/register` | — |
| POST | `/api/v1/login` | — |
| GET | `/api/v1/videos` | — |
| GET | `/api/v1/video/{id}` | — |
| POST | `/api/v1/watchlist` | JWT |
| GET | `/api/v1/analytics` | Admin |
| GET | `/api/v1/admin/revenue` | Admin |

---

## Database Tables

- `users` — accounts with JWT auth
- `admin_users` — admin privileges linked to users
- `videos` — 50 seeded titles (documentaries + shorts)
- `categories` — Legends, Rivalries, Stories, Secrets
- `watchlist` — user saved content
- `subscriptions` — free / premium / enterprise
- `analytics` — event tracking

---

## Deployment

### Frontend → Vercel

```bash
npm run build
vercel --prod
```

Set environment variable:
```
VITE_API_URL=https://your-api.up.railway.app/api/v1
```

Update `vercel.json` rewrite destination to your Railway URL.

### Backend → Railway

1. Create PostgreSQL service on Railway
2. Deploy `backend/` directory
3. Set env vars: `DATABASE_URL`, `SECRET_KEY`, `CORS_ORIGINS`
4. Railway runs `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

---

## Content (Seeded)

- UNTOLD: The Revolution
- UNTOLD: Rise of Dhoni
- UNTOLD: Messi vs Ronaldo
- UNTOLD: The Last Dance
- + 46 more documentaries & shorts

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 19, Tailwind CSS 4, Axios, Recharts |
| Backend | Python FastAPI, SQLAlchemy, JWT |
| Database | PostgreSQL 16 |
| Deploy | Vercel + Railway |
