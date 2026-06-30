import { useCallback, useEffect, useState } from 'react';
import { DEFAULT_RESEARCH_PREFERENCES } from '../constants';

const STORAGE_KEY = 'untold.research.preferences';

function readPrefs() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return { ...DEFAULT_RESEARCH_PREFERENCES };
    return { ...DEFAULT_RESEARCH_PREFERENCES, ...JSON.parse(raw) };
  } catch {
    return { ...DEFAULT_RESEARCH_PREFERENCES };
  }
}

export function useResearchPreferences() {
  const [prefs, setPrefs] = useState(readPrefs);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(prefs));
  }, [prefs]);

  const updatePref = useCallback((key, value) => {
    setPrefs((prev) => ({ ...prev, [key]: value }));
  }, []);

  const resetPrefs = useCallback(() => {
    setPrefs({ ...DEFAULT_RESEARCH_PREFERENCES });
  }, []);

  return { prefs, updatePref, resetPrefs };
}
