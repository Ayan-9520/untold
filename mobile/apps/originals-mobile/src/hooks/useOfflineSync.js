import { useEffect, useState, useCallback } from 'react';
import NetInfo from '@react-native-community/netinfo';
import { mobileApi, originalsApi } from '@untold/api';
import { syncOfflineQueues, getOfflineStatus } from '@untold/offline';

export function useOfflineSync(handlers) {
  const [online, setOnline] = useState(true);
  const [manifest, setManifest] = useState(null);
  const [lastSyncAt, setLastSyncAt] = useState(null);
  const [syncing, setSyncing] = useState(false);
  const [offlineStatus, setOfflineStatus] = useState({ stale: true, lastSyncAt: null });

  useEffect(() => {
    const unsub = NetInfo.addEventListener((state) => {
      setOnline(!!state.isConnected);
    });
    mobileApi.offlineManifest('originals').then(setManifest).catch(() => {});
    return () => unsub();
  }, []);

  const sync = useCallback(async () => {
    if (!online || !manifest) return;
    setSyncing(true);
    try {
      await syncOfflineQueues(manifest, handlers);
      const ts = Date.now();
      setLastSyncAt(ts);
      setOfflineStatus(await getOfflineStatus(manifest, ts));
    } finally {
      setSyncing(false);
    }
  }, [online, manifest, handlers]);

  useEffect(() => {
    if (online) sync();
  }, [online, sync]);

  return { online, manifest, syncing, lastSyncAt, sync, offlineStatus };
}

export const originalsOfflineHandlers = {
  watch_progress: (item) => originalsApi.trackEvent({ ...item, event_type: 'watch_progress' }),
  analytics_events: (item) => originalsApi.trackEvent(item),
};
