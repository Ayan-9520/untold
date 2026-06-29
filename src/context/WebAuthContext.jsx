import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { api } from '../api/client';

const TOKEN_KEY = 'untold-token';
const REFRESH_KEY = 'untold-refresh';

const WebAuthContext = createContext(null);

export function WebAuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const init = async () => {
      if (localStorage.getItem(TOKEN_KEY)) {
        try {
          const profile = await api.auth.me();
          setUser(profile);
        } catch {
          localStorage.removeItem(TOKEN_KEY);
          localStorage.removeItem(REFRESH_KEY);
        }
      }
      setLoading(false);
    };
    init();
  }, []);

  const login = useCallback(async ({ email, password }) => {
    const tokens = await api.auth.login({ email, password });
    localStorage.setItem(TOKEN_KEY, tokens.access_token);
    localStorage.setItem(REFRESH_KEY, tokens.refresh_token);
    const profile = await api.auth.me();
    setUser(profile);
    return profile;
  }, []);

  const register = useCallback(async ({ email, password, full_name }) => {
    await api.auth.register({ email, password, full_name });
    return login({ email, password });
  }, [login]);

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_KEY);
    setUser(null);
  }, []);

  return (
    <WebAuthContext.Provider value={{ user, loading, isAuthenticated: !!user, login, register, logout }}>
      {children}
    </WebAuthContext.Provider>
  );
}

export function useWebAuth() {
  const ctx = useContext(WebAuthContext);
  if (!ctx) throw new Error('useWebAuth must be used within WebAuthProvider');
  return ctx;
}
