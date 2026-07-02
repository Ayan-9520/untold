import React, { useCallback, useState } from 'react';
import { ScrollView, RefreshControl } from 'react-native';
import { originalsApi } from '@untold/api';
import { Screen, Title, Muted, VideoCard } from '../components/ui';

export default function WatchlistScreen({ navigation }) {
  const [items, setItems] = useState([]);
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(async () => {
    try {
      const data = await originalsApi.watchlist();
      setItems(data?.items ?? data ?? []);
    } catch {
      setItems([]);
    }
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
    load();
  }, [load]);

  return (
    <Screen>
      <ScrollView refreshControl={<RefreshControl refreshing={refreshing} onRefresh={refresh} tintColor="#e11d48" />}>
        <Title>Watchlist</Title>
        {!items.length && <Muted>Sign in to save titles for later.</Muted>}
        {items.map((item) => {
          const v = item.video || item;
          return (
            <VideoCard
              key={v.id}
              item={v}
              onPress={() => navigation.navigate('Player', { videoId: v.id })}
            />
          );
        })}
      </ScrollView>
    </Screen>
  );
}
