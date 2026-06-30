import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useCallback } from 'react';
import { studioPlatform } from '../../../api/adminApi';

export const publishingOverviewKey = ['publishing', 'overview'];
export const publishingQueueKey = (params) => ['publishing', 'queue', params];
export const publishingWorkspaceKey = (projectId) => ['publishing', 'workspace', projectId];

export function usePublishingOverview() {
  return useQuery({
    queryKey: publishingOverviewKey,
    queryFn: () => studioPlatform.getPublishingOverview(),
    staleTime: 15_000,
  });
}

export function usePublishingQueue(params = {}) {
  return useQuery({
    queryKey: publishingQueueKey(params),
    queryFn: () => studioPlatform.getPublishingQueue(params),
    staleTime: 5_000,
    refetchInterval: 10_000,
  });
}

export function usePublishingWorkspace(projectId) {
  return useQuery({
    queryKey: publishingWorkspaceKey(projectId),
    queryFn: () => studioPlatform.getPublishingWorkspace(projectId),
    enabled: Boolean(projectId),
  });
}

export function usePublishingMutations(projectId) {
  const qc = useQueryClient();
  const invalidate = useCallback(() => {
    qc.invalidateQueries({ queryKey: ['publishing'] });
    if (projectId) qc.invalidateQueries({ queryKey: publishingWorkspaceKey(projectId) });
  }, [qc, projectId]);

  const updatePackage = useMutation({
    mutationFn: (data) => studioPlatform.updatePublishingPackage(projectId, data),
    onSuccess: invalidate,
  });

  const schedule = useMutation({
    mutationFn: (data) => studioPlatform.schedulePublish(projectId, data),
    onSuccess: invalidate,
  });

  const approveJob = useMutation({
    mutationFn: ({ jobId, notes }) => studioPlatform.approvePublishJob(jobId, notes),
    onSuccess: invalidate,
  });

  const rejectJob = useMutation({
    mutationFn: ({ jobId, notes }) => studioPlatform.rejectPublishJob(jobId, notes),
    onSuccess: invalidate,
  });

  const retryJob = useMutation({
    mutationFn: (jobId) => studioPlatform.retryPublishJob(jobId),
    onSuccess: invalidate,
  });

  return { updatePackage, schedule, approveJob, rejectJob, retryJob, invalidate };
}
