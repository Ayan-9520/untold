export const AUTH_TOKEN_KEY = 'untold-studio-token';
export const AUTH_REFRESH_KEY = 'untold-studio-refresh';
export const THEME_KEY = 'untold-studio-theme';

export const API_BASE = import.meta.env.VITE_API_URL || '/api/v1';
export const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || '';

export const STUDIO_ROLES = [
  'admin',
  'producer',
  'researcher',
  'writer',
  'editor',
  'designer',
  'publisher',
  'viewer',
] as const;
