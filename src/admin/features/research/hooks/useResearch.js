import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useCallback, useRef } from 'react';
import { studioPlatform } from '../../../api/adminApi';

export const researchKey = (id) => ['research', id];
export const researchProjectKey = (projectId) => ['research', 'project', projectId];

export function useResearchByProject(projectId) {
  return useQuery({
    queryKey: researchProjectKey(projectId),
    queryFn: async () => {
      const ws = await studioPlatform.getResearchWorkspace(projectId);
      return studioPlatform.getResearch(ws.id);
    },
    enabled: Boolean(projectId),
    staleTime: 10_000,
  });
}

export function useResearch(researchId) {
  return useQuery({
    queryKey: researchKey(researchId),
    queryFn: () => studioPlatform.getResearch(researchId),
    enabled: Boolean(researchId),
  });
}

export function useResearchMutations(researchId, projectId) {
  const qc = useQueryClient();
  const invalidate = useCallback(() => {
    qc.invalidateQueries({ queryKey: researchKey(researchId) });
    if (projectId) qc.invalidateQueries({ queryKey: researchProjectKey(projectId) });
  }, [qc, researchId, projectId]);

  const autosave = useMutation({
    mutationFn: (content) => studioPlatform.autosaveResearch(researchId, { workspace_content: content }),
  });

  const saveVersion = useMutation({
    mutationFn: () => studioPlatform.saveResearchVersion(researchId),
    onSuccess: invalidate,
  });

  const restoreVersion = useMutation({
    mutationFn: (versionId) => studioPlatform.restoreResearchVersion(researchId, versionId),
    onSuccess: invalidate,
  });

  const runAI = useMutation({
    mutationFn: (payload) => studioPlatform.runResearchAI(researchId, typeof payload === 'string' ? { prompt: payload } : payload),
    onSuccess: invalidate,
  });

  const updateTopic = useMutation({
    mutationFn: (topic) => studioPlatform.updateResearchTopic(researchId, topic),
    onSuccess: invalidate,
  });

  const requestApproval = useMutation({
    mutationFn: () => studioPlatform.requestResearchApproval(researchId),
    onSuccess: invalidate,
  });

  const approveResearch = useMutation({
    mutationFn: () => studioPlatform.approveResearch(researchId),
    onSuccess: invalidate,
  });

  const rejectResearch = useMutation({
    mutationFn: (notes) => studioPlatform.rejectResearch(researchId, notes),
    onSuccess: invalidate,
  });

  const createNote = useMutation({
    mutationFn: (data) => studioPlatform.createNote(researchId, data),
    onSuccess: invalidate,
  });

  const addSource = useMutation({
    mutationFn: (data) => studioPlatform.addSource(researchId, data),
    onSuccess: invalidate,
  });

  const addBookmark = useMutation({
    mutationFn: (data) => studioPlatform.addBookmark(researchId, data),
    onSuccess: invalidate,
  });

  const addFactCheck = useMutation({
    mutationFn: (data) => studioPlatform.addFactCheck(researchId, data),
    onSuccess: invalidate,
  });

  const updateFactCheck = useMutation({
    mutationFn: ({ id, data }) => studioPlatform.updateFactCheck(researchId, id, data),
    onSuccess: invalidate,
  });

  const addComment = useMutation({
    mutationFn: (content) => studioPlatform.addResearchComment(researchId, { content }),
    onSuccess: invalidate,
  });

  const addTimeline = useMutation({
    mutationFn: (data) => studioPlatform.addTimelineEvent(researchId, data),
    onSuccess: invalidate,
  });

  return {
    autosave, saveVersion, restoreVersion, runAI,
    updateTopic, requestApproval, approveResearch, rejectResearch,
    createNote, addSource, addBookmark, addFactCheck, updateFactCheck,
    addComment, addTimeline, invalidate,
  };
}

export function useDebouncedAutosave(autosaveMutation, delay = 1500) {
  const timer = useRef(null);
  return useCallback((content) => {
    if (timer.current) clearTimeout(timer.current);
    timer.current = setTimeout(() => autosaveMutation.mutate(content), delay);
  }, [autosaveMutation, delay]);
}
