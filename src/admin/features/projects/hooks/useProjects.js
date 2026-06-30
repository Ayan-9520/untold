import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { studioPlatform } from '../../../api/adminApi';

export const PROJECTS_KEY = ['studio', 'projects'];
export const projectKey = (id) => ['studio', 'project', id];

export function useProjects(params = {}) {
  return useQuery({
    queryKey: [...PROJECTS_KEY, params],
    queryFn: () => studioPlatform.listProjects(params),
    staleTime: 15_000,
  });
}

export function useProject(id) {
  return useQuery({
    queryKey: projectKey(id),
    queryFn: () => studioPlatform.getProject(id),
    enabled: Boolean(id),
  });
}

export function useProjectComments(projectId) {
  return useQuery({
    queryKey: [...projectKey(projectId), 'comments'],
    queryFn: () => studioPlatform.listComments(projectId),
    enabled: Boolean(projectId),
  });
}

export function useProjectAttachments(projectId) {
  return useQuery({
    queryKey: [...projectKey(projectId), 'attachments'],
    queryFn: () => studioPlatform.listAttachments(projectId),
    enabled: Boolean(projectId),
  });
}

export function useProjectTimeline(projectId) {
  return useQuery({
    queryKey: [...projectKey(projectId), 'timeline'],
    queryFn: () => studioPlatform.getTimeline(projectId),
    enabled: Boolean(projectId),
  });
}

export function useCalendarFeed(from, to) {
  return useQuery({
    queryKey: ['studio', 'calendar', from, to],
    queryFn: () => studioPlatform.getCalendar(from, to),
    enabled: Boolean(from && to),
  });
}

export function useProjectMutations() {
  const qc = useQueryClient();

  const invalidate = (id) => {
    qc.invalidateQueries({ queryKey: PROJECTS_KEY });
    if (id) qc.invalidateQueries({ queryKey: projectKey(id) });
  };

  const create = useMutation({
    mutationFn: studioPlatform.createProject,
    onSuccess: () => invalidate(),
  });

  const update = useMutation({
    mutationFn: ({ id, data }) => studioPlatform.updateProject(id, data),
    onSuccess: (_, { id }) => invalidate(id),
  });

  const remove = useMutation({
    mutationFn: (id) => studioPlatform.deleteProject(id),
    onSuccess: () => invalidate(),
  });

  const assignMember = useMutation({
    mutationFn: ({ projectId, data }) => studioPlatform.assignMember(projectId, data),
    onSuccess: (_, { projectId }) => invalidate(projectId),
  });

  const removeMember = useMutation({
    mutationFn: ({ projectId, userId }) => studioPlatform.removeMember(projectId, userId),
    onSuccess: (_, { projectId }) => invalidate(projectId),
  });

  const addComment = useMutation({
    mutationFn: ({ projectId, content }) => studioPlatform.addComment(projectId, { content }),
    onSuccess: (_, { projectId }) => {
      qc.invalidateQueries({ queryKey: [...projectKey(projectId), 'comments'] });
      qc.invalidateQueries({ queryKey: [...projectKey(projectId), 'timeline'] });
    },
  });

  const addAttachment = useMutation({
    mutationFn: ({ projectId, data }) => studioPlatform.addAttachment(projectId, data),
    onSuccess: (_, { projectId }) => {
      qc.invalidateQueries({ queryKey: [...projectKey(projectId), 'attachments'] });
      invalidate(projectId);
    },
  });

  const deleteComment = useMutation({
    mutationFn: ({ projectId, commentId }) => studioPlatform.deleteComment(projectId, commentId),
    onSuccess: (_, { projectId }) => {
      qc.invalidateQueries({ queryKey: [...projectKey(projectId), 'comments'] });
      qc.invalidateQueries({ queryKey: [...projectKey(projectId), 'timeline'] });
    },
  });

  const deleteAttachment = useMutation({
    mutationFn: ({ projectId, attachmentId }) => studioPlatform.deleteAttachment(projectId, attachmentId),
    onSuccess: (_, { projectId }) => {
      qc.invalidateQueries({ queryKey: [...projectKey(projectId), 'attachments'] });
      invalidate(projectId);
    },
  });

  return { create, update, remove, assignMember, removeMember, addComment, addAttachment, deleteComment, deleteAttachment, invalidate };
}
