import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useCallback } from 'react';
import { studioPlatform } from '../../../api/adminApi';

export const voiceStudioKey = ['voice-studio'];
export const voiceQueueKey = ['voice-studio', 'queue'];
export const voiceHistoryKey = (lang) => ['voice-studio', 'history', lang || 'all'];
export const voicePromptsKey = (lang) => ['voice-studio', 'prompts', lang || 'all'];

export function useVoiceStudioOverview() {
  return useQuery({
    queryKey: voiceStudioKey,
    queryFn: () => studioPlatform.getVoiceStudioOverview(),
    staleTime: 15_000,
  });
}

export function useVoiceQueue() {
  return useQuery({
    queryKey: voiceQueueKey,
    queryFn: () => studioPlatform.getVoiceQueue(),
    refetchInterval: 3_000,
  });
}

export function useVoiceHistory(language) {
  return useQuery({
    queryKey: voiceHistoryKey(language),
    queryFn: () => studioPlatform.getVoiceHistory({ language, limit: 60 }),
    refetchInterval: 6_000,
  });
}

export function useVoicePrompts(language) {
  return useQuery({
    queryKey: voicePromptsKey(language),
    queryFn: () => studioPlatform.getVoicePrompts(language),
  });
}

export function useVoiceStudioMutations() {
  const qc = useQueryClient();
  const invalidate = useCallback(() => {
    qc.invalidateQueries({ queryKey: voiceStudioKey });
    qc.invalidateQueries({ queryKey: voiceQueueKey });
    qc.invalidateQueries({ queryKey: ['voice-studio', 'history'] });
  }, [qc]);

  const generate = useMutation({
    mutationFn: (data) => studioPlatform.createVoiceGeneration(data),
    onSuccess: invalidate,
  });

  const preview = useMutation({
    mutationFn: (data) => studioPlatform.previewVoice(data),
  });

  const translate = useMutation({
    mutationFn: (data) => studioPlatform.translateVoice(data),
  });

  const saveToAsset = useMutation({
    mutationFn: (id) => studioPlatform.saveVoiceToAsset(id),
  });

  const retryJob = useMutation({
    mutationFn: (id) => studioPlatform.retryVoiceJob(id),
    onSuccess: invalidate,
  });

  const cancelJob = useMutation({
    mutationFn: (id) => studioPlatform.cancelVoiceJob(id),
    onSuccess: invalidate,
  });

  return { generate, preview, translate, saveToAsset, retryJob, cancelJob, invalidate };
}
