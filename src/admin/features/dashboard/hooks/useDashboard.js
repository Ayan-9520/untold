import { useQuery } from '@tanstack/react-query';
import { fetchDashboardWithFallback } from '../api/fetchDashboard';

export const DASHBOARD_QUERY_KEY = ['studio', 'dashboard'];

export function useDashboard() {
  return useQuery({
    queryKey: DASHBOARD_QUERY_KEY,
    queryFn: fetchDashboardWithFallback,
    staleTime: 20_000,
    refetchInterval: 30_000,
    refetchOnWindowFocus: true,
  });
}
