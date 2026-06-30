import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useCallback } from 'react';
import { studioPlatform } from '../../../api/adminApi';

export const seoStudioKey = ['seo-studio'];
export const seoQueueKey = ['seo-studio', 'queue'];
export const seoHistoryKey = ['seo-studio', 'history'];

export function useSEOStudioOverview() {
  return useQuery({ queryKey: seoStudioKey, queryFn: () => studioPlatform.getSEOStudioOverview(), staleTime: 15_000 });
}

export function useSEOQueue() {
  return useQuery({ queryKey: seoQueueKey, queryFn: () => studioPlatform.getSEOQueue(), refetchInterval: 3_000 });
}

export function useSEOHistory() {
  return useQuery({ queryKey: seoHistoryKey, queryFn: () => studioPlatform.getSEOHistory({ limit: 60 }), refetchInterval: 6_000 });
}

export function useSEOStudioMutations() {
  const qc = useQueryClient();
  const invalidate = useCallback(() => {
    qc.invalidateQueries({ queryKey: seoStudioKey });
    qc.invalidateQueries({ queryKey: seoQueueKey });
    qc.invalidateQueries({ queryKey: seoHistoryKey });
  }, [qc]);

  return {
    generate: useMutation({ mutationFn: (d) => studioPlatform.createSEOGeneration(d), onSuccess: invalidate }),
    selectVariant: useMutation({ mutationFn: ({ id, variantId }) => studioPlatform.selectSEOVariant(id, variantId), onSuccess: invalidate }),
    requestApproval: useMutation({ mutationFn: ({ id, data }) => studioPlatform.requestSEOApproval(id, data), onSuccess: invalidate }),
    approve: useMutation({ mutationFn: ({ id, data }) => studioPlatform.approveSEO(id, data), onSuccess: invalidate }),
    reject: useMutation({ mutationFn: ({ id, data }) => studioPlatform.rejectSEO(id, data), onSuccess: invalidate }),
    applyToProject: useMutation({ mutationFn: ({ id, projectId, variantId }) => studioPlatform.applySEOToProject(id, { project_id: projectId, variant_id: variantId }), onSuccess: invalidate }),
    exportPack: (id, variantId) => studioPlatform.exportSEOPack(id, variantId),
    retryJob: useMutation({ mutationFn: (id) => studioPlatform.retrySEOJob(id), onSuccess: invalidate }),
    cancelJob: useMutation({ mutationFn: (id) => studioPlatform.cancelSEOJob(id), onSuccess: invalidate }),
    invalidate,
  };
}
