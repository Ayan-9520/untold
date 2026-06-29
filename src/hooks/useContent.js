import { useState, useEffect, useCallback } from 'react';
import { contentApi } from '../api/content';

export function useContent(fetcher, deps = []) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const refetch = useCallback(() => {
    setLoading(true);
    setError(null);
    fetcher()
      .then((res) => setData(res.data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, deps);

  useEffect(() => {
    refetch();
  }, [refetch]);

  return { data, loading, error, refetch };
}

export const useHero = () => useContent(() => contentApi.getHero());
export const useFeatured = () => useContent(() => contentApi.getFeatured());
export const useDocumentaries = () => useContent(() => contentApi.getDocumentaries());
export const useLegends = () => useContent(() => contentApi.getLegends());
export const useRivalries = () => useContent(() => contentApi.getRivalries());
export const useTrending = () => useContent(() => contentApi.getTrending());
export const useShorts = () => useContent(() => contentApi.getShorts());
