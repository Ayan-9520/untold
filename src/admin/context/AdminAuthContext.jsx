import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { auth, tenancy } from '../api/adminApi';

async function bootstrapTenancy() {
  try {
    const org = await tenancy.getCurrentOrganization();
    if (org?.id) await tenancy.setActiveOrg(org.id);
  } catch {
    try {
      const orgs = await tenancy.listOrganizations();
      if (orgs?.[0]?.id) await tenancy.setActiveOrg(orgs[0].id);
    } catch {
      /* org context optional until user joins an org */
    }
  }
}

const AdminAuthContext = createContext(null);

function userHasStudioAccess(profile) {
  if (!profile) return false;
  if (profile.has_studio_access != null) return !!profile.has_studio_access;
  return !!(profile.is_admin || profile.studio_role);
}

export function AdminAuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const init = async () => {
      if (auth.isAuthenticated()) {
        try {
          const profile = await auth.getMe();
          if (userHasStudioAccess(profile)) {
            setUser(profile);
            await bootstrapTenancy();
          } else {
            auth.logout();
          }
        } catch {
          auth.logout();
        }
      }
      setLoading(false);
    };
    init();
  }, []);

  const login = useCallback(async (email, password) => {
    const profile = await auth.login(email, password);
    if (!userHasStudioAccess(profile)) {
      auth.logout();
      throw new Error('Studio access required');
    }
    setUser(profile);
    await bootstrapTenancy();
    return profile;
  }, []);

  const logout = useCallback(() => {
    auth.logout();
    setUser(null);
  }, []);

  return (
    <AdminAuthContext.Provider
      value={{
        user,
        loading,
        isAuthenticated: !!user,
        isAdmin: user?.is_admin ?? false,
        hasStudioAccess: userHasStudioAccess(user),
        studioRole: user?.studio_role ?? null,
        permissions: user?.permissions ?? [],
        login,
        logout,
      }}
    >
      {children}
    </AdminAuthContext.Provider>
  );
}

export function useAdminAuth() {
  const ctx = useContext(AdminAuthContext);
  if (!ctx) throw new Error('useAdminAuth must be used within AdminAuthProvider');
  return ctx;
}
