import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useWebAuth } from './WebAuthContext';
import viewerApi from '../api/viewer';

const STORAGE_KEY = 'untold-active-profile';
const ViewerProfileContext = createContext(null);

export function ViewerProfileProvider({ children }) {
  const { isAuthenticated } = useWebAuth();
  const [profiles, setProfiles] = useState([]);
  const [activeProfile, setActiveProfile] = useState(null);
  const [loading, setLoading] = useState(false);

  const loadProfiles = useCallback(async () => {
    if (!isAuthenticated) {
      setProfiles([]);
      setActiveProfile(null);
      return;
    }
    setLoading(true);
    try {
      const list = await viewerApi.listProfiles();
      setProfiles(list);
      const stored = localStorage.getItem(STORAGE_KEY);
      const found = list.find((p) => String(p.id) === stored) || list.find((p) => p.is_primary) || list[0];
      setActiveProfile(found || null);
    } catch {
      setProfiles([]);
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated]);

  useEffect(() => {
    loadProfiles();
  }, [loadProfiles]);

  const selectProfile = useCallback((profile) => {
    setActiveProfile(profile);
    localStorage.setItem(STORAGE_KEY, String(profile.id));
  }, []);

  const createProfile = useCallback(async (data) => {
    const profile = await viewerApi.createProfile(data);
    await loadProfiles();
    selectProfile(profile);
    return profile;
  }, [loadProfiles, selectProfile]);

  return (
    <ViewerProfileContext.Provider
      value={{ profiles, activeProfile, loading, selectProfile, createProfile, reloadProfiles: loadProfiles }}
    >
      {children}
    </ViewerProfileContext.Provider>
  );
}

export function useViewerProfile() {
  const ctx = useContext(ViewerProfileContext);
  if (!ctx) throw new Error('useViewerProfile must be used within ViewerProfileProvider');
  return ctx;
}
