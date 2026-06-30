import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { studioPlatform } from '../../../api/adminApi';

const adminKey = ['admin'];

export function useAdminOverview() {
  return useQuery({ queryKey: [...adminKey, 'overview'], queryFn: () => studioPlatform.getAdminOverview(), staleTime: 15_000 });
}

export function useAdminSection(section, fetcher) {
  return useQuery({
    queryKey: [...adminKey, section],
    queryFn: fetcher,
    staleTime: 10_000,
  });
}

export function useAdminMutations() {
  const qc = useQueryClient();
  const invalidate = () => qc.invalidateQueries({ queryKey: adminKey });

  const createApiKey = useMutation({
    mutationFn: (data) => studioPlatform.createApiKey(data),
    onSuccess: invalidate,
  });
  const revokeApiKey = useMutation({
    mutationFn: (id) => studioPlatform.revokeApiKey(id),
    onSuccess: invalidate,
  });
  const toggleFlag = useMutation({
    mutationFn: ({ id, enabled }) => studioPlatform.updateFeatureFlag(id, { enabled }),
    onSuccess: invalidate,
  });
  const createBackup = useMutation({
    mutationFn: (label) => studioPlatform.createBackup(label),
    onSuccess: invalidate,
  });

  return { createApiKey, revokeApiKey, toggleFlag, createBackup, invalidate };
}
