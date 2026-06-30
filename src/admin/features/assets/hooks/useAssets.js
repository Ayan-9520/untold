import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useCallback } from 'react';
import { studioPlatform } from '../../../api/adminApi';

export const assetsOverviewKey = ['assets', 'overview'];
export const assetsListKey = (params) => ['assets', 'list', params];
export const collectionsKey = ['assets', 'collections'];

export function useAssetsOverview() {
  return useQuery({
    queryKey: assetsOverviewKey,
    queryFn: () => studioPlatform.getAssetsOverview(),
    staleTime: 15_000,
  });
}

export function useAssetsList(params) {
  return useQuery({
    queryKey: assetsListKey(params),
    queryFn: () => studioPlatform.listAssets(params),
    staleTime: 5_000,
  });
}

export function useAssetCollections() {
  return useQuery({
    queryKey: collectionsKey,
    queryFn: () => studioPlatform.listAssetCollections(),
  });
}

export function useAssetMutations() {
  const qc = useQueryClient();
  const invalidate = useCallback(() => {
    qc.invalidateQueries({ queryKey: ['assets'] });
  }, [qc]);

  const upload = useMutation({
    mutationFn: (formData) => studioPlatform.uploadAsset(formData),
    onSuccess: invalidate,
  });

  const update = useMutation({
    mutationFn: ({ id, data }) => studioPlatform.updateAsset(id, data),
    onSuccess: invalidate,
  });

  const toggleFavorite = useMutation({
    mutationFn: (id) => studioPlatform.toggleAssetFavorite(id),
    onSuccess: invalidate,
  });

  const remove = useMutation({
    mutationFn: (id) => studioPlatform.deleteAsset(id),
    onSuccess: invalidate,
  });

  const restore = useMutation({
    mutationFn: (id) => studioPlatform.restoreAsset(id),
    onSuccess: invalidate,
  });

  const restoreVersion = useMutation({
    mutationFn: ({ assetId, versionId }) => studioPlatform.restoreAssetVersion(assetId, versionId),
    onSuccess: invalidate,
  });

  const createCollection = useMutation({
    mutationFn: (data) => studioPlatform.createAssetCollection(data),
    onSuccess: invalidate,
  });

  const addPermission = useMutation({
    mutationFn: ({ assetId, data }) => studioPlatform.addAssetPermission(assetId, data),
    onSuccess: invalidate,
  });

  return {
    upload, update, toggleFavorite, remove, restore, restoreVersion, createCollection, addPermission, invalidate,
  };
}

export function useAssetVersions(assetId) {
  return useQuery({
    queryKey: ['assets', assetId, 'versions'],
    queryFn: () => studioPlatform.getAssetVersions(assetId),
    enabled: Boolean(assetId),
  });
}

export function useAssetPermissions(assetId) {
  return useQuery({
    queryKey: ['assets', assetId, 'permissions'],
    queryFn: () => studioPlatform.getAssetPermissions(assetId),
    enabled: Boolean(assetId),
  });
}
