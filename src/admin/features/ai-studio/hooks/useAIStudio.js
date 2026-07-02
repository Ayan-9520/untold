import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useCallback } from 'react';
import { studioPlatform } from '../../../api/adminApi';

export const aiStudioKey = ['ai-studio'];
export const aiQueueKey = ['ai-studio', 'queue'];
export const aiHistoryKey = (module) => ['ai-studio', 'history', module || 'all'];
export const aiTelemetryKey = (module) => ['ai-studio', 'telemetry', module || 'all'];
export const aiPromptsKey = (module) => ['ai-studio', 'prompts', module || 'all'];

export function useAIStudioOverview() {
  return useQuery({
    queryKey: aiStudioKey,
    queryFn: () => studioPlatform.getAIStudioOverview(),
    staleTime: 15_000,
  });
}

export function useAIQueue() {
  return useQuery({
    queryKey: aiQueueKey,
    queryFn: () => studioPlatform.getAIQueue(),
    refetchInterval: 5_000,
  });
}

export function useAIHistory(module) {
  return useQuery({
    queryKey: aiHistoryKey(module),
    queryFn: () => studioPlatform.getAIHistory({ module }),
    refetchInterval: 10_000,
  });
}

export function useAITelemetry(module) {
  return useQuery({
    queryKey: aiTelemetryKey(module),
    queryFn: () => studioPlatform.getAITelemetry({ module }),
    refetchInterval: 15_000,
  });
}

export function useAIPrompts(module) {
  return useQuery({
    queryKey: aiPromptsKey(module),
    queryFn: () => studioPlatform.getAIPrompts(module),
  });
}

export function useAIStudioMutations() {
  const qc = useQueryClient();
  const invalidate = useCallback(() => {
    qc.invalidateQueries({ queryKey: aiStudioKey });
    qc.invalidateQueries({ queryKey: aiQueueKey });
    qc.invalidateQueries({ queryKey: ['ai-studio', 'history'] });
    qc.invalidateQueries({ queryKey: ['ai-studio', 'telemetry'] });
  }, [qc]);

  const generate = useMutation({
    mutationFn: (data) => studioPlatform.createAIGeneration(data),
    onSuccess: invalidate,
  });

  const retryJob = useMutation({
    mutationFn: (id) => studioPlatform.retryAIJob(id),
    onSuccess: invalidate,
  });

  const cancelJob = useMutation({
    mutationFn: (id) => studioPlatform.cancelAIJob(id),
    onSuccess: invalidate,
  });

  const createPrompt = useMutation({
    mutationFn: (data) => studioPlatform.createAIPrompt(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['ai-studio', 'prompts'] }),
  });

  return { generate, retryJob, cancelJob, createPrompt, invalidate };
}
