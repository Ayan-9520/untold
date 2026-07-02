import React from 'react';
import { View, Text, StyleSheet, Image, Pressable } from 'react-native';

const colors = {
  bg: '#0a0a0a',
  card: '#171717',
  border: '#262626',
  text: '#fafafa',
  muted: '#a3a3a3',
  accent: '#e11d48',
};

export function Screen({ children, style }) {
  return <View style={[styles.screen, style]}>{children}</View>;
}

export function Title({ children }) {
  return <Text style={styles.title}>{children}</Text>;
}

export function Muted({ children, style }) {
  return <Text style={[styles.muted, style]}>{children}</Text>;
}

export function OfflineBanner({ online, syncing }) {
  if (online && !syncing) return null;
  return (
    <View style={[styles.banner, !online && styles.bannerOffline]}>
      <Text style={styles.bannerText}>
        {!online ? 'Offline — progress saved locally' : 'Syncing…'}
      </Text>
    </View>
  );
}

export function VideoCard({ item, onPress }) {
  return (
    <Pressable onPress={onPress} style={styles.videoCard}>
      {item.thumbnail_url ? (
        <Image source={{ uri: item.thumbnail_url }} style={styles.thumb} />
      ) : (
        <View style={[styles.thumb, styles.thumbPlaceholder]} />
      )}
      <View style={styles.videoMeta}>
        <Text style={styles.videoTitle} numberOfLines={2}>
          {item.title}
        </Text>
        <Muted>{item.video_type || 'original'}</Muted>
      </View>
    </Pressable>
  );
}

export function PrimaryButton({ title, onPress }) {
  return (
    <Text onPress={onPress} style={styles.button}>
      {title}
    </Text>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.bg, padding: 16 },
  title: { color: colors.text, fontSize: 22, fontWeight: '700', marginBottom: 12 },
  muted: { color: colors.muted, fontSize: 14 },
  banner: { backgroundColor: '#f59e0b', padding: 8, borderRadius: 8, marginBottom: 12 },
  bannerOffline: { backgroundColor: '#7f1d1d' },
  bannerText: { color: '#fff', textAlign: 'center', fontWeight: '600' },
  videoCard: {
    flexDirection: 'row',
    backgroundColor: colors.card,
    borderRadius: 12,
    marginBottom: 10,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: colors.border,
  },
  thumb: { width: 120, height: 68 },
  thumbPlaceholder: { backgroundColor: '#262626' },
  videoMeta: { flex: 1, padding: 10, justifyContent: 'center' },
  videoTitle: { color: colors.text, fontWeight: '600', marginBottom: 4 },
  button: {
    backgroundColor: colors.accent,
    color: '#fff',
    textAlign: 'center',
    padding: 14,
    borderRadius: 10,
    fontWeight: '700',
    marginTop: 12,
  },
});

export { colors };
