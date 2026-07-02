import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

const colors = {
  bg: '#0a0a0a',
  card: '#171717',
  border: '#262626',
  text: '#fafafa',
  muted: '#a3a3a3',
  accent: '#e11d48',
  success: '#22c55e',
  warn: '#f59e0b',
};

export function Screen({ children, style }) {
  return <View style={[styles.screen, style]}>{children}</View>;
}

export function Card({ children, style }) {
  return <View style={[styles.card, style]}>{children}</View>;
}

export function Title({ children }) {
  return <Text style={styles.title}>{children}</Text>;
}

export function Muted({ children }) {
  return <Text style={styles.muted}>{children}</Text>;
}

export function StatGrid({ items }) {
  return (
    <View style={styles.statGrid}>
      {items.map((item) => (
        <View key={item.label} style={styles.stat}>
          <Text style={styles.statValue}>{item.value}</Text>
          <Text style={styles.statLabel}>{item.label}</Text>
        </View>
      ))}
    </View>
  );
}

export function OfflineBanner({ online, syncing }) {
  if (online && !syncing) return null;
  return (
    <View style={[styles.banner, !online && styles.bannerOffline]}>
      <Text style={styles.bannerText}>
        {!online ? 'Offline — actions queued' : 'Syncing…'}
      </Text>
    </View>
  );
}

export function PrimaryButton({ title, onPress, disabled }) {
  return (
    <Text
      onPress={disabled ? undefined : onPress}
      style={[styles.button, disabled && styles.buttonDisabled]}
    >
      {title}
    </Text>
  );
}

export function ErrorText({ children }) {
  if (!children) return null;
  return <Text style={styles.error}>{children}</Text>;
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.bg, padding: 16 },
  card: {
    backgroundColor: colors.card,
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: colors.border,
  },
  title: { color: colors.text, fontSize: 22, fontWeight: '700', marginBottom: 12 },
  muted: { color: colors.muted, fontSize: 14 },
  statGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  stat: {
    width: '47%',
    backgroundColor: colors.card,
    borderRadius: 10,
    padding: 12,
    borderWidth: 1,
    borderColor: colors.border,
  },
  statValue: { color: colors.accent, fontSize: 24, fontWeight: '700' },
  statLabel: { color: colors.muted, fontSize: 12, marginTop: 4 },
  banner: {
    backgroundColor: colors.warn,
    padding: 8,
    borderRadius: 8,
    marginBottom: 12,
  },
  bannerOffline: { backgroundColor: '#7f1d1d' },
  bannerText: { color: '#fff', textAlign: 'center', fontWeight: '600' },
  button: {
    backgroundColor: colors.accent,
    color: '#fff',
    textAlign: 'center',
    padding: 14,
    borderRadius: 10,
    fontWeight: '700',
    overflow: 'hidden',
  },
  buttonDisabled: { opacity: 0.5 },
  error: { color: '#f87171', marginTop: 8 },
});

export { colors };
