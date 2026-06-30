import { useQuery } from '@tanstack/react-query';
import { studioPlatform } from '../../../api/adminApi';

export const analyticsOverviewKey = ['analytics', 'overview'];
export const analyticsRealtimeKey = ['analytics', 'realtime'];

export function useAnalyticsOverview() {
  return useQuery({
    queryKey: analyticsOverviewKey,
    queryFn: () => studioPlatform.getAnalyticsOverview(),
    staleTime: 30_000,
  });
}

export function useAnalyticsRealtime() {
  return useQuery({
    queryKey: analyticsRealtimeKey,
    queryFn: () => studioPlatform.getAnalyticsRealtime(),
    staleTime: 5_000,
    refetchInterval: 10_000,
  });
}
