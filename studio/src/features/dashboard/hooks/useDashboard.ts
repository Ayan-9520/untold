import { useQuery } from '@tanstack/react-query';
import { studioApi } from '@/api/studio';

export const DASHBOARD_QUERY_KEY = ['studio-dashboard'] as const;

export function useDashboard() {
  return useQuery({
    queryKey: DASHBOARD_QUERY_KEY,
    queryFn: studioApi.dashboard,
    refetchInterval: 30_000,
    staleTime: 20_000,
  });
}
