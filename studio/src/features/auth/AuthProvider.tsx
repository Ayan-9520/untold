import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';
import { authApi } from './api';
import type { LoginCredentials, StudioRole, StudioUser } from './types';
import { authStorage } from '@/lib/auth-storage';
import { canAccess } from '@/lib/permissions';

interface AuthContextValue {
  user: StudioUser | null;
  loading: boolean;
  isAuthenticated: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  loginWithGoogle: (idToken: string) => Promise<void>;
  logout: () => void;
  hasPermission: (permission: string) => boolean;
  hasRole: (roles: StudioRole[]) => boolean;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<StudioUser | null>(null);
  const [loading, setLoading] = useState(true);

  const refreshUser = useCallback(async () => {
    const token = authStorage.getToken();
    if (!token) {
      setUser(null);
      setLoading(false);
      return;
    }
    try {
      const me = await authApi.studioMe();
      setUser(me);
    } catch {
      authStorage.clear();
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshUser();
  }, [refreshUser]);

  const login = useCallback(async (credentials: LoginCredentials) => {
    const tokens = await authApi.login(credentials);
    authStorage.setTokens(tokens.access_token, tokens.refresh_token);
    const me = await authApi.studioMe();
    setUser(me);
  }, []);

  const loginWithGoogle = useCallback(async (idToken: string) => {
    const tokens = await authApi.googleLogin(idToken);
    authStorage.setTokens(tokens.access_token, tokens.refresh_token);
    const me = await authApi.studioMe();
    setUser(me);
  }, []);

  const logout = useCallback(() => {
    authStorage.clear();
    setUser(null);
  }, []);

  const hasPermission = useCallback(
    (permission: string) => {
      if (!user) return false;
      return canAccess(permission, user.studio_role, user.permissions);
    },
    [user]
  );

  const hasRole = useCallback(
    (roles: StudioRole[]) => {
      if (!user) return false;
      if (user.studio_role === 'admin') return true;
      return roles.includes(user.studio_role);
    },
    [user]
  );

  const value = useMemo(
    () => ({
      user,
      loading,
      isAuthenticated: Boolean(user),
      login,
      loginWithGoogle,
      logout,
      hasPermission,
      hasRole,
      refreshUser,
    }),
    [user, loading, login, loginWithGoogle, logout, hasPermission, hasRole, refreshUser]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
