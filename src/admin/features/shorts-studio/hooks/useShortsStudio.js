import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useCallback } from 'react';
import { studioPlatform } from '../../../api/adminApi';

export const shortsStudioKey = ['shorts-studio'];
export const shortsQueueKey = ['shorts-studio', 'queue'];
export const shortsHistoryKey = ['shorts-studio', 'history'];

export function useShortsStudioOverview() {
  return useQuery({ queryKey: shortsStudioKey, queryFn: () => studioPlatform.getShortsStudioOverview(), staleTime: 15_000 });
}

export function useShortsQueue() {
  return useQuery({ queryKey: shortsQueueKey, queryFn: () => studioPlatform.getShortsQueue(), refetchInterval: 3_000 });
}

export function useShortsHistory() {
  return useQuery({ queryKey: shortsHistoryKey, queryFn: () => studioPlatform.getShortsHistory({ limit: 60 }), refetchInterval: 6_000 });
}

export function useShortsStudioMutations() {
  const qc = useQueryClient();
  const invalidate = useCallback(() => {
    qc.invalidateQueries({ queryKey: shortsStudioKey });
    qc.invalidateQueries({ queryKey: shortsQueueKey });
    qc.invalidateQueries({ queryKey: shortsHistoryKey });
  }, [qc]);

  return {
    generate: useMutation({ mutationFn: (d) => studioPlatform.createShortsGeneration(d), onSuccess: invalidate }),
    queuePublish: useMutation({ mutationFn: ({ id, data }) => studioPlatform.queueShortsPublish(id, data), onSuccess: invalidate }),
    saveToAsset: useMutation({ mutationFn: (id) => studioPlatform.saveShortsToAsset(id) }),
    retryJob: useMutation({ mutationFn: (id) => studioPlatform.retryShortsJob(id), onSuccess: invalidate }),
    cancelJob: useMutation({ mutationFn: (id) => studioPlatform.cancelShortsJob(id), onSuccess: invalidate }),
    invalidate,
  };
}
