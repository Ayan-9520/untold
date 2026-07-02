import React, { useCallback, useState } from 'react';
import { ScrollView, RefreshControl } from 'react-native';
import { mobileApi } from '@untold/api';
import { Screen, Title, StatGrid, Muted } from '../components/ui';

export default function AnalyticsScreen() {
  const [data, setData] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(async () => {
    const overview = await mobileApi.studioAnalytics();
    setData(overview);
  }, []);

  const refresh = async () => {
    setRefreshing(true);
    try {
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
        { label: 'Total views', value: data.views ?? '—' },
        { label: 'Watch hours', value: data.watch_time_hours ?? '—' },
        { label: 'Subscribers', value: data.subscribers ?? data.active_subscriptions ?? '—' },
        { label: 'CTR %', value: data.ctr ?? '—' },
      ]
    : [{ label: 'Loading…', value: '—' }];

  return (
    <Screen>
      <ScrollView refreshControl={<RefreshControl refreshing={refreshing} onRefresh={refresh} tintColor="#e11d48" />}>
        <Title>Analytics</Title>
        <StatGrid items={stats} />
        {data?.top_videos && (
          <>
            <Muted style={{ marginTop: 16 }}>Top videos</Muted>
            {data.top_videos.slice(0, 5).map((p) => (
              <Muted key={p.id ?? p.title}>
                {p.title}: {p.views ?? p.views_count ?? 0} views
              </Muted>
            ))}
          </>
        )}
      </ScrollView>
    </Screen>
  );
}
