import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useCallback } from 'react';
import { studioPlatform } from '../../../api/adminApi';

export const imageStudioKey = ['image-studio'];
export const imageQueueKey = ['image-studio', 'queue'];
export const imageHistoryKey = (type) => ['image-studio', 'history', type || 'all'];
export const imageFavoritesKey = ['image-studio', 'favorites'];
export const imageCollectionsKey = ['image-studio', 'collections'];
export const imagePromptsKey = (type) => ['image-studio', 'prompts', type || 'all'];

export function useImageStudioOverview() {
  return useQuery({
    queryKey: imageStudioKey,
    queryFn: () => studioPlatform.getImageStudioOverview(),
    staleTime: 15_000,
  });
}

export function useImageQueue() {
  return useQuery({
    queryKey: imageQueueKey,
    queryFn: () => studioPlatform.getImageQueue(),
    refetchInterval: 5_000,
  });
}

export function useImageHistory(imageType) {
  return useQuery({
    queryKey: imageHistoryKey(imageType),
    queryFn: () => studioPlatform.getImageHistory({ image_type: imageType, limit: 60 }),
    refetchInterval: 8_000,
  });
}

export function useImageFavorites() {
  return useQuery({
    queryKey: imageFavoritesKey,
    queryFn: () => studioPlatform.getImageFavorites(),
  });
}

export function useImageCollections() {
  return useQuery({
    queryKey: imageCollectionsKey,
    queryFn: () => studioPlatform.getImageCollections(),
  });
}

export function useImagePrompts(imageType) {
  return useQuery({
    queryKey: imagePromptsKey(imageType),
    queryFn: () => studioPlatform.getImagePrompts(imageType),
  });
}

export function useImageStudioMutations() {
  const qc = useQueryClient();
  const invalidate = useCallback(() => {
    qc.invalidateQueries({ queryKey: imageStudioKey });
    qc.invalidateQueries({ queryKey: imageQueueKey });
    qc.invalidateQueries({ queryKey: ['image-studio', 'history'] });
    qc.invalidateQueries({ queryKey: imageFavoritesKey });
    qc.invalidateQueries({ queryKey: imageCollectionsKey });
  }, [qc]);

  const generate = useMutation({
    mutationFn: (data) => studioPlatform.createImageGeneration(data),
    onSuccess: invalidate,
  });

  const toggleFavorite = useMutation({
    mutationFn: (id) => studioPlatform.toggleImageFavorite(id),
    onSuccess: invalidate,
  });

  const upscale = useMutation({
    mutationFn: (id) => studioPlatform.upscaleImage(id),
    onSuccess: invalidate,
  });

  const vary = useMutation({
    mutationFn: ({ id, prompt }) => studioPlatform.varyImage(id, prompt ? { prompt } : {}),
    onSuccess: invalidate,
  });

  const saveToAsset = useMutation({
    mutationFn: (id) => studioPlatform.saveImageToAsset(id),
  });

  const createCollection = useMutation({
    mutationFn: (data) => studioPlatform.createImageCollection(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: imageCollectionsKey }),
  });

  const addToCollection = useMutation({
    mutationFn: ({ collectionId, generationId }) => studioPlatform.addImageToCollection(collectionId, generationId),
    onSuccess: () => qc.invalidateQueries({ queryKey: imageCollectionsKey }),
  });

  const retryJob = useMutation({
    mutationFn: (id) => studioPlatform.retryImageJob(id),
    onSuccess: invalidate,
  });

  const cancelJob = useMutation({
    mutationFn: (id) => studioPlatform.cancelImageJob(id),
    onSuccess: invalidate,
  });

  return {
    generate, toggleFavorite, upscale, vary, saveToAsset,
    createCollection, addToCollection, retryJob, cancelJob, invalidate,
  };
}
