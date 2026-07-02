import React, { useCallback, useState } from 'react';
import { ScrollView, Text, RefreshControl } from 'react-native';
import { mobileApi } from '@untold/api';
import { Screen, Title, Card, Muted, colors } from '../components/ui';

export default function AiJobsScreen() {
  const [queue, setQueue] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(async () => {
    const data = await mobileApi.studioAiJobs();
    setQueue(data);
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

  const queued = queue?.queued ?? [];
  const running = queue?.running ?? [];
  const jobs = [...running, ...queued];

  return (
    <Screen>
      <ScrollView refreshControl={<RefreshControl refreshing={refreshing} onRefresh={refresh} tintColor="#e11d48" />}>
        <Title>AI jobs</Title>
        <Muted>
          Running: {running.length} · Queued: {queued.length}
        </Muted>
        {!jobs.length && <Muted style={{ marginTop: 12 }}>No active jobs</Muted>}
        {jobs.map((job) => (
          <Card key={job.id}>
            <Text style={{ color: colors.text, fontWeight: '600' }}>
              {job.project_title || job.module || `Job #${job.id}`}
            </Text>
            <Muted>
              {String(job.status)} · {job.provider || 'AI'}
            </Muted>
          </Card>
        ))}
      </ScrollView>
    </Screen>
  );
}
