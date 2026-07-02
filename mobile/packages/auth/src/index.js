const TOKEN_KEY = 'untold-mobile-token';
const REFRESH_KEY = 'untold-mobile-refresh';
const USER_KEY = 'untold-mobile-user';

let storage = {
  async getItem(key) {
    return null;
  },
  async setItem(key, value) {
    /* noop */
  },
  async removeItem(key) {
    /* noop */
  },
};

export function configureAuthStore(store) {
  storage = store;
}

export async function saveSession({ access_token, refresh_token }, user = null) {
  if (access_token) await storage.setItem(TOKEN_KEY, access_token);
  if (refresh_token) await storage.setItem(REFRESH_KEY, refresh_token);
  if (user) await storage.setItem(USER_KEY, JSON.stringify(user));
}

export async function getAccessToken() {
  return storage.getItem(TOKEN_KEY);
}

export async function getRefreshToken() {
  return storage.getItem(REFRESH_KEY);
}

export async function getStoredUser() {
  const raw = await storage.getItem(USER_KEY);
  return raw ? JSON.parse(raw) : null;
}

export async function isAuthenticated() {
  return !!(await getAccessToken());
}

export async function clearSession() {
  await storage.removeItem(TOKEN_KEY);
  await storage.removeItem(REFRESH_KEY);
  await storage.removeItem(USER_KEY);
}

export async function loginWithApi(authApi, email, password, { studio = false } = {}) {
  const tokens = await authApi.login(email, password);
  await saveSession(tokens);
  const me = studio ? await authApi.studioMe() : await authApi.originalsMe();
  await saveSession(tokens, me);
  return me;
}
