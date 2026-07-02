# UNTOLD Mobile Platform

Production-ready React Native apps for **UNTOLD Studio** and **UNTOLD Originals**, backed by `/api/v1/mobile/*` endpoints.

## Apps

| App | Path | Purpose |
|-----|------|---------|
| **UNTOLD Studio Mobile** | `mobile/apps/studio-mobile` | Dashboard, project approvals, AI jobs, analytics, media upload |
| **UNTOLD Originals Mobile** | `mobile/apps/originals-mobile` | Home catalog, HLS player, watchlist, offline watch progress |

## Shared packages

| Package | Path | Role |
|---------|------|------|
| `@untold/api` | `mobile/packages/api` | Axios client — auth, mobile, originals endpoints |
| `@untold/auth` | `mobile/packages/auth` | Secure token storage + login helpers |
| `@untold/offline` | `mobile/packages/offline` | AsyncStorage queues for offline sync |

## Backend API

Prefix: `/api/v1/mobile`

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/devices/register` | Register Expo/FCM push token |
| `DELETE` | `/devices/{id}` | Unregister device |
| `GET` | `/offline-manifest?app_type=studio\|originals` | Cache hints + sync queues |
| `GET` | `/studio/overview` | Studio dashboard stats |
| `GET` | `/studio/approvals` | Pending approval inbox |
| `POST` | `/studio/approvals/{id}/action` | Approve / reject |
| `GET` | `/studio/ai-jobs` | AI generation queue |
| `GET` | `/studio/analytics` | Studio analytics overview |
| `POST` | `/studio/assets/upload` | Multipart media upload |
| `GET` | `/originals/home` | Featured + recent videos |

### Database (migration `046`)

- `mobile_devices` — push tokens per user/app
- `mobile_push_log` — delivery audit log

Push dispatch is logged via `MobilePushService`; wire FCM/APNs credentials in production.

## Features

### Offline mode

Clients fetch `/mobile/offline-manifest` and queue actions locally:

- **Studio:** `approval_actions`, `analytics_events`
- **Originals:** `watch_progress`, `analytics_events`

Queues flush automatically when connectivity returns (`@react-native-community/netinfo`).

### Push notifications

On login, apps call `POST /mobile/devices/register` with Expo push token. Approval actions trigger push to the requester via `MobilePushService.notify_user`.

### Project approval

Studio Mobile **Approvals** tab loads pending items and supports approve/reject inline or queued offline.

### Analytics

Studio Mobile surfaces `StudioAnalyticsService.get_overview`. Originals tracks watch progress via `/analytics/events`.

### Media upload

Studio Mobile uses `expo-document-picker` → `POST /mobile/studio/assets/upload` (wraps `AssetLibraryService.upload_asset`).

### AI jobs

Studio Mobile **AI Jobs** tab reads `AIStudioService.get_queue`.

## Quick start

```bash
cd mobile
npm install

# Studio app (Expo)
npm run studio

# Originals app
npm run originals
```

Set API URL in each app's `app.json` → `expo.extra.apiUrl` (default `http://localhost:8000/api/v1`).

Run backend migration:

```bash
cd backend
alembic upgrade head
```

## Production checklist

- [ ] Set `expo.extra.apiUrl` to production API
- [ ] Configure FCM (Android) / APNs (iOS) in `MobilePushService._dispatch`
- [ ] EAS Build for store binaries (`eas build`)
- [ ] Enable push notification credentials in Expo dashboard
- [ ] Use HTTPS and certificate pinning for API in hardened builds
