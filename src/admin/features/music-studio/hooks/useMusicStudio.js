import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useCallback } from 'react';
import { studioPlatform } from '../../../api/adminApi';

export const musicStudioKey = ['music-studio'];
export const musicQueueKey = ['music-studio', 'queue'];
export const musicHistoryKey = (cat) => ['music-studio', 'history', cat || 'all'];
export const musicFavoritesKey = ['music-studio', 'favorites'];
export const musicPromptsKey = (cat) => ['music-studio', 'prompts', cat || 'all'];

export function useMusicStudioOverview() {
  return useQuery({
    queryKey: musicStudioKey,
    queryFn: () => studioPlatform.getMusicStudioOverview(),
    staleTime: 15_000,
  });
}

export function useMusicQueue() {
  return useQuery({
    queryKey: musicQueueKey,
    queryFn: () => studioPlatform.getMusicQueue(),
    refetchInterval: 3_000,
  });
}

export function useMusicHistory(category) {
  return useQuery({
    queryKey: musicHistoryKey(category),
    queryFn: () => studioPlatform.getMusicHistory({ category, limit: 60 }),
    refetchInterval: 6_000,
  });
}

export function useMusicFavorites() {
  return useQuery({
    queryKey: musicFavoritesKey,
    queryFn: () => studioPlatform.getMusicFavorites(),
  });
}

export function useMusicPrompts(category) {
  return useQuery({
    queryKey: musicPromptsKey(category),
    queryFn: () => studioPlatform.getMusicPrompts(category),
  });
}

export function useMusicStudioMutations() {
  const qc = useQueryClient();
  const invalidate = useCallback(() => {
    qc.invalidateQueries({ queryKey: musicStudioKey });
    qc.invalidateQueries({ queryKey: musicQueueKey });
    qc.invalidateQueries({ queryKey: ['music-studio', 'history'] });
    qc.invalidateQueries({ queryKey: musicFavoritesKey });
  }, [qc]);

  const generate = useMutation({
    mutationFn: (data) => studioPlatform.createMusicGeneration(data),
    onSuccess: invalidate,
  });

  const preview = useMutation({
    mutationFn: (data) => studioPlatform.previewMusic(data),
  });

  const toggleFavorite = useMutation({
    mutationFn: (id) => studioPlatform.toggleMusicFavorite(id),
    onSuccess: invalidate,
  });

  const saveToAsset = useMutation({
    mutationFn: (id) => studioPlatform.saveMusicToAsset(id),
  });

  const retryJob = useMutation({
    mutationFn: (id) => studioPlatform.retryMusicJob(id),
    onSuccess: invalidate,
  });

  const cancelJob = useMutation({
    mutationFn: (id) => studioPlatform.cancelMusicJob(id),
    onSuccess: invalidate,
  });

  return {
    generate, preview, toggleFavorite, saveToAsset, retryJob, cancelJob, invalidate,
  };
}
