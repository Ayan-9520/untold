/**
 * Runtime API configuration — single source for frontend ↔ backend URLs.
 * Production Docker/nginx builds use relative paths (/api/v1).
 */

function trimSlash(value) {
  return (value || '').replace(/\/+$/, '');
}

export function getApiBase() {
  const configured = import.meta.env.VITE_API_URL?.trim();
  if (configured) return trimSlash(configured);
  if (import.meta.env.PROD) return '/api/v1';
  return 'http://localhost:8000/api/v1';
}

export function getWsBase() {
  const configured = import.meta.env.VITE_WS_URL?.trim();
  if (configured) return trimSlash(configured);
  const api = getApiBase();
  if (api.startsWith('/')) {
    if (typeof window === 'undefined') return 'ws://localhost';
    const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    return `${proto}//${window.location.host}`;
  }
  const origin = trimSlash(api.replace(/\/api\/v1\/?$/, ''));
  return origin.replace(/^http/, 'ws');
}

export function apiUrl(path = '') {
  const base = getApiBase();
  const suffix = path.startsWith('/') ? path : `/${path}`;
  return `${base}${suffix}`;
}
