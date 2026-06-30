import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useCallback } from 'react';
import { studioPlatform } from '../../../api/adminApi';

export const videoStudioKey = ['video-studio'];
export const videoQueueKey = ['video-studio', 'queue'];
export const videoHistoryKey = (type) => ['video-studio', 'history', type || 'all'];
export const videoPromptsKey = (type) => ['video-studio', 'prompts', type || 'all'];

export function useVideoStudioOverview() {
  return useQuery({
    queryKey: videoStudioKey,
    queryFn: () => studioPlatform.getVideoStudioOverview(),
    staleTime: 15_000,
  });
}

export function useVideoQueue() {
  return useQuery({
    queryKey: videoQueueKey,
    queryFn: () => studioPlatform.getVideoQueue(),
    refetchInterval: 3_000,
  });
}

export function useVideoHistory(videoType) {
  return useQuery({
    queryKey: videoHistoryKey(videoType),
    queryFn: () => studioPlatform.getVideoHistory({ video_type: videoType, limit: 60 }),
    refetchInterval: 6_000,
  });
}

export function useVideoPrompts(videoType) {
  return useQuery({
    queryKey: videoPromptsKey(videoType),
    queryFn: () => studioPlatform.getVideoPrompts(videoType),
  });
}

export function useVideoStudioMutations() {
  const qc = useQueryClient();
  const invalidate = useCallback(() => {
    qc.invalidateQueries({ queryKey: videoStudioKey });
    qc.invalidateQueries({ queryKey: videoQueueKey });
    qc.invalidateQueries({ queryKey: ['video-studio', 'history'] });
  }, [qc]);

  const generate = useMutation({
    mutationFn: (data) => studioPlatform.createVideoGeneration(data),
    onSuccess: invalidate,
  });

  const saveToAsset = useMutation({
    mutationFn: (id) => studioPlatform.saveVideoToAsset(id),
  });

  const retryJob = useMutation({
    mutationFn: (id) => studioPlatform.retryVideoJob(id),
    onSuccess: invalidate,
  });

  const cancelJob = useMutation({
    mutationFn: (id) => studioPlatform.cancelVideoJob(id),
    onSuccess: invalidate,
  });

  return { generate, saveToAsset, retryJob, cancelJob, invalidate };
}
