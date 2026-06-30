import client from './client';
import type { DashboardData, Notification, Project } from '@/types/studio';

export const studioApi = {
  dashboard: () => client.get<DashboardData>('/studio/platform/dashboard').then((r) => r.data),
  projects: (params?: { stage?: string }) =>
    client.get<{ items: Project[]; total: number }>('/studio/platform/projects', { params }).then((r) => r.data),
  createProject: (data: { title: string; category?: string; stage?: string }) =>
    client.post<Project>('/studio/platform/projects', data).then((r) => r.data),
  publishProject: (id: number) =>
    client.post<Project>(`/studio/platform/projects/${id}/publish`).then((r) => r.data),
  notifications: () =>
    client.get<Notification[]>('/studio/platform/notifications').then((r) => r.data),
};
