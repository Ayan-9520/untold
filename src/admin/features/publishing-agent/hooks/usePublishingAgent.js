import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useCallback } from 'react';
import { studioPlatform } from '../../../api/adminApi';

export const publishingAgentKey = ['publishing-agent'];
export const publishingAgentQueueKey = ['publishing-agent', 'queue'];
export const publishingAgentHistoryKey = ['publishing-agent', 'history'];
export const publishingAgentAnalyticsKey = ['publishing-agent', 'analytics'];
export const publishingAgentWebhooksKey = ['publishing-agent', 'webhooks'];

export function usePublishingAgentOverview() {
  return useQuery({
    queryKey: publishingAgentKey,
    queryFn: () => studioPlatform.getPublishingAgentOverview(),
    staleTime: 15_000,
  });
}

export function usePublishingAgentQueue() {
  return useQuery({
    queryKey: publishingAgentQueueKey,
    queryFn: () => studioPlatform.getPublishingAgentQueue(),
    refetchInterval: 4_000,
  });
}

export function usePublishingAgentHistory() {
  return useQuery({
    queryKey: publishingAgentHistoryKey,
    queryFn: () => studioPlatform.getPublishingAgentHistory({ limit: 50 }),
    refetchInterval: 8_000,
  });
}

export function usePublishingAgentAnalytics(days = 30) {
  return useQuery({
    queryKey: [...publishingAgentAnalyticsKey, days],
    queryFn: () => studioPlatform.getPublishingAgentAnalytics({ days }),
    staleTime: 30_000,
  });
}

export function usePublishingAgentWebhooks() {
  return useQuery({
    queryKey: publishingAgentWebhooksKey,
    queryFn: () => studioPlatform.listPublishingWebhooks(),
    staleTime: 15_000,
  });
}

export function usePublishingAgentMutations() {
  const qc = useQueryClient();
  const invalidate = useCallback(() => {
    qc.invalidateQueries({ queryKey: publishingAgentKey });
    qc.invalidateQueries({ queryKey: publishingAgentQueueKey });
    qc.invalidateQueries({ queryKey: publishingAgentHistoryKey });
    qc.invalidateQueries({ queryKey: publishingAgentAnalyticsKey });
    qc.invalidateQueries({ queryKey: publishingAgentWebhooksKey });
    qc.invalidateQueries({ queryKey: ['publishing'] });
  }, [qc]);

  return {
    dispatch: useMutation({
      mutationFn: (d) => studioPlatform.dispatchPublishingAgent(d),
      onSuccess: invalidate,
    }),
    approveRun: useMutation({
      mutationFn: ({ id, notes }) => studioPlatform.approvePublishingRun(id, notes),
      onSuccess: invalidate,
    }),
    rejectRun: useMutation({
      mutationFn: ({ id, notes }) => studioPlatform.rejectPublishingRun(id, notes),
      onSuccess: invalidate,
    }),
    retryRun: useMutation({
      mutationFn: ({ id, jobIds }) => studioPlatform.retryPublishingRun(id, jobIds),
      onSuccess: invalidate,
    }),
    retryJob: useMutation({
      mutationFn: (jobId) => studioPlatform.retryPublishJob(jobId),
      onSuccess: invalidate,
    }),
    approveJob: useMutation({
      mutationFn: (jobId) => studioPlatform.approvePublishJob(jobId),
      onSuccess: invalidate,
    }),
    rejectJob: useMutation({
      mutationFn: (jobId) => studioPlatform.rejectPublishJob(jobId),
      onSuccess: invalidate,
    }),
    createWebhook: useMutation({
      mutationFn: (d) => studioPlatform.createPublishingWebhook(d),
      onSuccess: invalidate,
    }),
    deleteWebhook: useMutation({
      mutationFn: (id) => studioPlatform.deletePublishingWebhook(id),
      onSuccess: invalidate,
    }),
    invalidate,
  };
}
