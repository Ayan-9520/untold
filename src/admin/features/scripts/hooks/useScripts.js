import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useCallback, useRef } from 'react';
import { studioPlatform } from '../../../api/adminApi';

export const scriptKey = (id) => ['script', id];
export const scriptProjectKey = (projectId) => ['script', 'project', projectId];

export function useScriptByProject(projectId) {
  return useQuery({
    queryKey: scriptProjectKey(projectId),
    queryFn: async () => {
      const ws = await studioPlatform.getScriptWorkspace(projectId);
      return studioPlatform.getScript(ws.id);
    },
    enabled: Boolean(projectId),
    staleTime: 5_000,
    refetchInterval: 8_000,
  });
}

export function useScript(scriptId) {
  return useQuery({
    queryKey: scriptKey(scriptId),
    queryFn: () => studioPlatform.getScript(scriptId),
    enabled: Boolean(scriptId),
    refetchInterval: 8_000,
  });
}

export function useScriptMutations(scriptId, projectId) {
  const qc = useQueryClient();
  const versionRef = useRef(null);

  const invalidate = useCallback(() => {
    qc.invalidateQueries({ queryKey: scriptKey(scriptId) });
    if (projectId) qc.invalidateQueries({ queryKey: scriptProjectKey(projectId) });
  }, [qc, scriptId, projectId]);

  const autosave = useMutation({
    mutationFn: ({ content, style, expected_version }) =>
      studioPlatform.autosaveScript(scriptId, { content, style, expected_version }),
    onSuccess: (data) => {
      versionRef.current = data.content_version;
    },
  });

  const heartbeat = useMutation({
    mutationFn: () => studioPlatform.scriptHeartbeat(scriptId),
  });

  const saveVersion = useMutation({
    mutationFn: (label) => studioPlatform.saveScriptVersion(scriptId, label ? { snapshot_label: label } : {}),
    onSuccess: invalidate,
  });

  const restoreVersion = useMutation({
    mutationFn: (versionId) => studioPlatform.restoreScriptVersion(scriptId, versionId),
    onSuccess: invalidate,
  });

  const addComment = useMutation({
    mutationFn: (content) => studioPlatform.addScriptComment(scriptId, { content }),
    onSuccess: invalidate,
  });

  const requestApproval = useMutation({
    mutationFn: (data) => studioPlatform.requestScriptApproval(scriptId, data),
    onSuccess: invalidate,
  });

  const approveScript = useMutation({
    mutationFn: (data) => studioPlatform.approveScript(scriptId, data),
    onSuccess: invalidate,
  });

  const rejectScript = useMutation({
    mutationFn: (data) => studioPlatform.rejectScript(scriptId, data),
    onSuccess: invalidate,
  });

  const runAI = useMutation({
    mutationFn: (data) => studioPlatform.runScriptAI(scriptId, data),
    onSuccess: invalidate,
  });

  return {
    autosave,
    heartbeat,
    saveVersion,
    restoreVersion,
    addComment,
    requestApproval,
    approveScript,
    rejectScript,
    runAI,
    invalidate,
    versionRef,
  };
}

export function useDebouncedScriptAutosave(autosaveMutation, getExpectedVersion, delay = 1500) {
  const timer = useRef(null);
  return useCallback(
    (content, style) => {
      if (timer.current) clearTimeout(timer.current);
      timer.current = setTimeout(() => {
        autosaveMutation.mutate({
          content,
          style,
          expected_version: getExpectedVersion(),
        });
      }, delay);
    },
    [autosaveMutation, getExpectedVersion, delay],
  );
}
