import React, { useCallback, useState } from 'react';
import { RefreshControl, ScrollView } from 'react-native';
import { mobileApi } from '@untold/api';
import { Screen, Title, StatGrid, OfflineBanner } from '../components/ui';
import { useOfflineSync, studioOfflineHandlers } from '../hooks/useOfflineSync';

export default function DashboardScreen() {
  const [data, setData] = useState(null);
  const [refreshing, setRefreshing] = useState(false);
  const { online, syncing, sync } = useOfflineSync('studio', studioOfflineHandlers);

  const load = useCallback(async () => {
    const overview = await mobileApi.studioOverview();
    setData(overview);
  }, []);

  const refresh = async () => {
    setRefreshing(true);
    try {
      await sync();
      await load();
    } finally {
      setRefreshing(false);
    }
  };

  React.useEffect(() => {
    load().catch(() => {});
  }, [load]);

  const stats = data
    ? [
        { label: 'Active projects', value: data.active_projects },
        { label: 'Pending approvals', value: data.pending_approvals },
        { label: 'AI jobs running', value: data.ai_jobs_running },
        { label: 'Unread alerts', value: data.unread_notifications },
      ]
    : [];

  return (
    <Screen>
      <OfflineBanner online={online} syncing={syncing} />
      <ScrollView refreshControl={<RefreshControl refreshing={refreshing} onRefresh={refresh} tintColor="#e11d48" />}>
        <Title>Studio overview</Title>
        <StatGrid items={stats.length ? stats : [{ label: 'Loading…', value: '—' }]} />
      </ScrollView>
    </Screen>
  );
}
