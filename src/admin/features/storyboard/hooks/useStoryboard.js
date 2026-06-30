import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useCallback } from 'react';
import { studioPlatform } from '../../../api/adminApi';

export const storyboardKey = (projectId) => ['storyboard', projectId];

export function useStoryboard(projectId) {
  return useQuery({
    queryKey: storyboardKey(projectId),
    queryFn: () => studioPlatform.getStoryboard(projectId),
    enabled: Boolean(projectId),
    staleTime: 5_000,
  });
}

export function useStoryboardMutations(projectId) {
  const qc = useQueryClient();
  const invalidate = useCallback(() => {
    qc.invalidateQueries({ queryKey: storyboardKey(projectId) });
  }, [qc, projectId]);

  const importFromScript = useMutation({
    mutationFn: (data) => studioPlatform.importStoryboardFromScript(projectId, data),
    onSuccess: invalidate,
  });

  const generateAI = useMutation({
    mutationFn: (data) => studioPlatform.generateStoryboardAI(projectId, data),
    onSuccess: invalidate,
  });

  const createScene = useMutation({
    mutationFn: (data) => studioPlatform.createStoryboardScene(projectId, data),
    onSuccess: invalidate,
  });

  const updateScene = useMutation({
    mutationFn: ({ sceneId, data }) => studioPlatform.updateStoryboardScene(projectId, sceneId, data),
    onSuccess: invalidate,
  });

  const deleteScene = useMutation({
    mutationFn: (sceneId) => studioPlatform.deleteStoryboardScene(projectId, sceneId),
    onSuccess: invalidate,
  });

  const reorderScenes = useMutation({
    mutationFn: (sceneIds) => studioPlatform.reorderStoryboardScenes(projectId, { scene_ids: sceneIds }),
    onSuccess: invalidate,
  });

  const saveRevision = useMutation({
    mutationFn: (label) => studioPlatform.saveStoryboardRevision(projectId, label ? { label } : {}),
    onSuccess: invalidate,
  });

  const restoreRevision = useMutation({
    mutationFn: (revisionId) => studioPlatform.restoreStoryboardRevision(projectId, revisionId),
    onSuccess: invalidate,
  });

  const requestApproval = useMutation({
    mutationFn: (data) => studioPlatform.requestStoryboardApproval(projectId, data),
    onSuccess: invalidate,
  });

  const approveStoryboard = useMutation({
    mutationFn: (data) => studioPlatform.approveStoryboard(projectId, data),
    onSuccess: invalidate,
  });

  const rejectStoryboard = useMutation({
    mutationFn: (data) => studioPlatform.rejectStoryboard(projectId, data),
    onSuccess: invalidate,
  });

  return {
    importFromScript,
    generateAI,
    createScene,
    updateScene,
    deleteScene,
    reorderScenes,
    saveRevision,
    restoreRevision,
    requestApproval,
    approveStoryboard,
    rejectStoryboard,
    invalidate,
  };
}
