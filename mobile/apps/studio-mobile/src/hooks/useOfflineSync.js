import { useEffect, useState, useCallback } from 'react';
import NetInfo from '@react-native-community/netinfo';
import { mobileApi, originalsApi } from '@untold/api';
import { syncOfflineQueues, getOfflineStatus } from '@untold/offline';

export function useOfflineSync(appType, handlers) {
  const [online, setOnline] = useState(true);
  const [manifest, setManifest] = useState(null);
  const [lastSyncAt, setLastSyncAt] = useState(null);
  const [syncing, setSyncing] = useState(false);
  const [offlineStatus, setOfflineStatus] = useState({ stale: true, lastSyncAt: null });

  useEffect(() => {
    const unsub = NetInfo.addEventListener((state) => {
      setOnline(!!state.isConnected);
    });
    mobileApi.offlineManifest(appType).then(setManifest).catch(() => {});
    return () => unsub();
  }, [appType]);

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

export const studioOfflineHandlers = {
  approval_actions: (item) =>
    mobileApi.studioApprovalAction(item.approval_id, item.action, item.notes),
  analytics_events: (item) => originalsApi.trackEvent(item),
};

export const originalsOfflineHandlers = {
  watch_progress: (item) => originalsApi.trackEvent({ ...item, event_type: 'watch_progress' }),
  analytics_events: (item) => originalsApi.trackEvent(item),
};
