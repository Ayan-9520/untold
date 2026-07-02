import React, { useEffect, useRef, useState } from 'react';
import { ActivityIndicator, View } from 'react-native';
import { Video } from 'expo-av';
import { originalsApi } from '@untold/api';
import { enqueue } from '@untold/offline';
import { Screen, Title, Muted, PrimaryButton, colors } from '../components/ui';
import { useOfflineSync, originalsOfflineHandlers } from '../hooks/useOfflineSync';

export default function PlayerScreen({ route, navigation }) {
  const { videoId } = route.params;
  const [video, setVideo] = useState(null);
  const [loading, setLoading] = useState(true);
  const ref = useRef(null);
  const { online } = useOfflineSync(originalsOfflineHandlers);

  useEffect(() => {
    originalsApi
      .video(videoId)
      .then(setVideo)
      .finally(() => setLoading(false));
  }, [videoId]);

  const onProgress = async (status) => {
    if (!status.isLoaded || !status.positionMillis) return;
    const payload = {
      video_id: videoId,
      position_ms: status.positionMillis,
      duration_ms: status.durationMillis,
    };
    if (online) {
      originalsApi.trackEvent({ event_type: 'watch_progress', ...payload });
    } else {
      await enqueue('watch_progress', payload);
    }
  };

  const toggleWatchlist = async () => {
    if (online) {
      await originalsApi.toggleWatchlist(videoId);
    }
  };

  if (loading) {
    return (
      <Screen>
        <ActivityIndicator color={colors.accent} />
      </Screen>
    );
  }

  const streamUrl = video?.hls_url || video?.stream_url || video?.video_url;

  return (
    <Screen>
      <Title>{video?.title || 'Now playing'}</Title>
      {streamUrl ? (
        <Video
          ref={ref}
          source={{ uri: streamUrl }}
          useNativeControls
          resizeMode="contain"
          style={{ width: '100%', aspectRatio: 16 / 9, backgroundColor: '#000' }}
          onPlaybackStatusUpdate={onProgress}
        />
      ) : (
        <Muted>No stream URL available for this title.</Muted>
      )}
      <Muted style={{ marginTop: 12 }}>{video?.description}</Muted>
      <PrimaryButton title="Add to watchlist" onPress={toggleWatchlist} />
      <PrimaryButton title="Back" onPress={() => navigation.goBack()} />
    </Screen>
  );
}
