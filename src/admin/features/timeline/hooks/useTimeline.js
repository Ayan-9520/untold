import { useCallback, useEffect, useRef, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { studioPlatform } from '../../../api/adminApi';
import { TimelineEngine } from '../engine';

export const timelineKey = (projectId) => ['timeline', projectId];

export function useTimelineWorkspace(projectId) {
  return useQuery({
    queryKey: timelineKey(projectId),
    queryFn: () => studioPlatform.getTimelineWorkspace(projectId),
    enabled: Boolean(projectId),
    staleTime: 10_000,
  });
}

export function useTimelineExports(projectId) {
  return useQuery({
    queryKey: ['timeline', projectId, 'exports'],
    queryFn: () => studioPlatform.listTimelineExports(projectId),
    enabled: Boolean(projectId),
    refetchInterval: 5000,
  });
}

export function useTimelineMutations(projectId) {
  const qc = useQueryClient();
  const invalidate = useCallback(() => {
    qc.invalidateQueries({ queryKey: timelineKey(projectId) });
    qc.invalidateQueries({ queryKey: ['timeline', projectId, 'exports'] });
  }, [qc, projectId]);

  const save = useMutation({
    mutationFn: (data) => studioPlatform.saveTimeline(projectId, data),
    onSuccess: invalidate,
  });

  const createExport = useMutation({
    mutationFn: (data) => studioPlatform.createTimelineExport(projectId, data),
    onSuccess: invalidate,
  });

  const createSnapshot = useMutation({
    mutationFn: (label) => studioPlatform.createTimelineSnapshot(projectId, label),
  });

  return { save, createExport, createSnapshot, invalidate };
}

/**
 * Bridges TimelineEngine (pure) with React state + autosave.
 */
export function useTimelineEditor(projectId, workspace) {
  const engineRef = useRef(null);
  const [snapshot, setSnapshot] = useState(null);
  const saveTimer = useRef(null);
  const mutations = useTimelineMutations(projectId);
  const lastSavedVersion = useRef(null);

  if (!engineRef.current) {
    engineRef.current = new TimelineEngine();
  }

  const loadedRef = useRef(null);

  useEffect(() => {
    if (!workspace) return;
    if (loadedRef.current === workspace.project_id) return;
    loadedRef.current = workspace.project_id;
    engineRef.current.loadDocument(workspace.document, {
      playhead: workspace.playhead,
      zoom: workspace.zoom,
      clearHistory: true,
    });
    lastSavedVersion.current = workspace.version;
    setSnapshot(engineRef.current.getSnapshot());
  }, [workspace]);

  useEffect(() => {
    const engine = engineRef.current;
    const unsub = engine.subscribe((snap) => {
      setSnapshot(snap);
      if (saveTimer.current) clearTimeout(saveTimer.current);
      saveTimer.current = setTimeout(() => {
        mutations.save.mutate({
          document: snap.document,
          playhead: snap.playhead,
          zoom: snap.zoom,
          autosave: true,
        });
      }, 2500);
    });
    return () => {
      unsub();
      if (saveTimer.current) clearTimeout(saveTimer.current);
    };
  }, [mutations.save]);

  useEffect(() => () => engineRef.current?.destroy(), []);

  const saveNow = useCallback(() => {
    const snap = engineRef.current.getSnapshot();
    mutations.save.mutate({
      document: snap.document,
      playhead: snap.playhead,
      zoom: snap.zoom,
      autosave: false,
    });
  }, [mutations.save]);

  return {
    engine: engineRef.current,
    snapshot,
    saveNow,
    saving: mutations.save.isPending,
    lastSaved: workspace?.last_auto_saved_at,
    createExport: mutations.createExport,
    createSnapshot: mutations.createSnapshot,
  };
}
