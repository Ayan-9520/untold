import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { authApi } from '../../api/appApi';

const AUTH_KEY = 'untold-token';
const USER_KEY = 'untold-user';

const AuthContext = createContext(null);

export function AppAuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const init = async () => {
      if (localStorage.getItem(AUTH_KEY)) {
        try {
          const { data } = await authApi.getProfile();
          setUser(data);
        } catch {
          localStorage.removeItem(AUTH_KEY);
        }
      }
      setLoading(false);
    };
    init();
  }, []);

  const login = useCallback(async (credentials) => {
    const { data } = await authApi.login(credentials);
    localStorage.setItem(AUTH_KEY, data.token);
    localStorage.setItem(USER_KEY, JSON.stringify(data.user));
    setUser(data.user);
    return data.user;
  }, []);

  const register = useCallback(async (credentials) => {
    const { data } = await authApi.register(credentials);
    localStorage.setItem(AUTH_KEY, data.token);
    localStorage.setItem(USER_KEY, JSON.stringify(data.user));
    setUser(data.user);
    return data.user;
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem(AUTH_KEY);
    localStorage.removeItem(USER_KEY);
    localStorage.removeItem('untold-refresh');
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider
      value={{ user, loading, isAuthenticated: !!user, login, register, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AppAuthProvider');
  return ctx;
}
