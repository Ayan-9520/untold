import React, { useCallback, useState } from 'react';
import { ScrollView, RefreshControl } from 'react-native';
import { mobileApi } from '@untold/api';
import { Screen, Title, Muted, VideoCard, OfflineBanner } from '../components/ui';
import { useOfflineSync, originalsOfflineHandlers } from '../hooks/useOfflineSync';

export default function HomeScreen({ navigation }) {
  const [data, setData] = useState({ featured: [], recent: [] });
  const [refreshing, setRefreshing] = useState(false);
  const { online, syncing, sync } = useOfflineSync(originalsOfflineHandlers);

  const load = useCallback(async () => {
    const home = await mobileApi.originalsHome();
    setData(home);
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

  return (
    <Screen>
      <OfflineBanner online={online} syncing={syncing} />
      <ScrollView refreshControl={<RefreshControl refreshing={refreshing} onRefresh={refresh} tintColor="#e11d48" />}>
        <Title>UNTOLD Originals</Title>
        <Muted style={{ marginBottom: 8 }}>Featured</Muted>
        {data.featured.map((v) => (
          <VideoCard key={`f-${v.id}`} item={v} onPress={() => navigation.navigate('Player', { videoId: v.id })} />
        ))}
        <Muted style={{ marginTop: 16, marginBottom: 8 }}>Recently added</Muted>
        {data.recent.map((v) => (
          <VideoCard key={`r-${v.id}`} item={v} onPress={() => navigation.navigate('Player', { videoId: v.id })} />
        ))}
      </ScrollView>
    </Screen>
  );
}
