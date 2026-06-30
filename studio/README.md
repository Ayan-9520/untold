# UNTOLD Studio — Production OS

React 19 + TypeScript foundation for internal content production.

## Stack

- React 19 · TypeScript · Vite · Tailwind CSS
- Shadcn-style UI · React Query · React Router
- React Hook Form · Zod · Framer Motion
- FastAPI · PostgreSQL · Docker · JWT · Google OAuth · RBAC

## Folder structure

```
studio/src/
├── app/                    # App shell & routes
│   ├── App.tsx
│   └── routes.tsx
├── api/
│   ├── client.ts           # Axios + JWT interceptors
│   └── studio.ts           # Studio platform API
├── components/
│   ├── layout/             # AppShell, Sidebar, Topbar
│   ├── routing/            # ProtectedRoute, RoleRoute
│   └── ui/                 # Button, Card, Input, Badge (shadcn)
├── config/
│   └── navigation.ts       # Sidebar nav + role gates
├── features/
│   └── auth/               # Login, Google, AuthProvider
├── lib/
│   ├── auth-storage.ts
│   ├── constants.ts
│   └── permissions.ts
├── pages/                  # Feature pages
├── providers/
│   ├── ThemeProvider.tsx   # Dark / light mode
│   └── query-client.ts
└── types/
```

## Run

```bash
cd studio
cp .env.example .env
npm install
npm run dev
```

Open **http://localhost:5174**

```bash
cd ../backend
docker compose up --build
```

## Auth

| Method | Endpoint |
|--------|----------|
| Email + password | `POST /api/v1/login` |
| Google | `POST /api/v1/auth/google` |
| Studio profile | `GET /api/v1/auth/studio/me` |

**Default admin:** `admin@untold.com` / `ChangeMe123!`

### Google login

1. Create OAuth client in [Google Cloud Console](https://console.cloud.google.com/)
2. Add authorized origin: `http://localhost:5174`
3. Set env:

```env
# studio/.env
VITE_GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com

# backend/.env
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
```

## RBAC roles

`admin` · `producer` · `researcher` · `writer` · `editor` · `designer` · `publisher` · `viewer`

- Sidebar items filtered by role
- `RoleRoute` guards sensitive pages
- Permissions from `backend/app/domain/studio/rbac.py`

## Theme

Premium **black + gold** (default). Toggle via topbar sun/moon icon. Persisted in `localStorage`.
