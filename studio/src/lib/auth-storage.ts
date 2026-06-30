import { AUTH_REFRESH_KEY, AUTH_TOKEN_KEY } from './constants';

export const authStorage = {
  getToken: () => localStorage.getItem(AUTH_TOKEN_KEY),
  setTokens: (access: string, refresh?: string) => {
    localStorage.setItem(AUTH_TOKEN_KEY, access);
    if (refresh) localStorage.setItem(AUTH_REFRESH_KEY, refresh);
  },
  clear: () => {
    localStorage.removeItem(AUTH_TOKEN_KEY);
    localStorage.removeItem(AUTH_REFRESH_KEY);
  },
};
