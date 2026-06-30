import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useCallback } from 'react';
import { studioPlatform } from '../../../api/adminApi';

export const translationStudioKey = ['translation-studio'];
export const translationQueueKey = ['translation-studio', 'queue'];
export const translationHistoryKey = ['translation-studio', 'history'];
export const translationMemoryKey = ['translation-studio', 'memory'];

export function useTranslationStudioOverview() {
  return useQuery({
    queryKey: translationStudioKey,
    queryFn: () => studioPlatform.getTranslationStudioOverview(),
    staleTime: 15_000,
  });
}

export function useTranslationQueue() {
  return useQuery({
    queryKey: translationQueueKey,
    queryFn: () => studioPlatform.getTranslationQueue(),
    refetchInterval: 3_000,
  });
}

export function useTranslationHistory() {
  return useQuery({
    queryKey: translationHistoryKey,
    queryFn: () => studioPlatform.getTranslationHistory({ limit: 60 }),
    refetchInterval: 6_000,
  });
}

export function useTranslationMemory(filters = {}) {
  return useQuery({
    queryKey: [...translationMemoryKey, filters],
    queryFn: () => studioPlatform.getTranslationMemory(filters),
    staleTime: 10_000,
  });
}

export function useTranslationStudioMutations() {
  const qc = useQueryClient();
  const invalidate = useCallback(() => {
    qc.invalidateQueries({ queryKey: translationStudioKey });
    qc.invalidateQueries({ queryKey: translationQueueKey });
    qc.invalidateQueries({ queryKey: translationHistoryKey });
    qc.invalidateQueries({ queryKey: translationMemoryKey });
  }, [qc]);

  return {
    translate: useMutation({
      mutationFn: (d) => studioPlatform.createTranslation(d),
      onSuccess: invalidate,
    }),
    requestApproval: useMutation({
      mutationFn: ({ id, data }) => studioPlatform.requestTranslationApproval(id, data),
      onSuccess: invalidate,
    }),
    approve: useMutation({
      mutationFn: ({ id, data }) => studioPlatform.approveTranslation(id, data),
      onSuccess: invalidate,
    }),
    reject: useMutation({
      mutationFn: ({ id, data }) => studioPlatform.rejectTranslation(id, data),
      onSuccess: invalidate,
    }),
    deleteMemory: useMutation({
      mutationFn: (entryId) => studioPlatform.deleteTranslationMemory(entryId),
      onSuccess: invalidate,
    }),
    retryJob: useMutation({
      mutationFn: (id) => studioPlatform.retryTranslationJob(id),
      onSuccess: invalidate,
    }),
    cancelJob: useMutation({
      mutationFn: (id) => studioPlatform.cancelTranslationJob(id),
      onSuccess: invalidate,
    }),
    getSrtUrl: (id) => studioPlatform.getTranslationSrtUrl(id),
    getVttUrl: (id) => studioPlatform.getTranslationVttUrl(id),
    invalidate,
  };
}
