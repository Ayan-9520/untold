export type StudioRole =
  | 'admin'
  | 'producer'
  | 'researcher'
  | 'writer'
  | 'editor'
  | 'designer'
  | 'publisher'
  | 'viewer';

export interface Project {
  id: number;
  slug: string;
  title: string;
  description: string | null;
  category: string | null;
  language: string;
  tags: string[] | null;
  stage: string;
  status: string;
  publishing_status: string;
  assignee: string;
  owner_id: number | null;
  sources_count: number;
  version: number;
  video_id: number | null;
  created_at: string;
  updated_at: string | null;
}

export interface DashboardOverview {
  active_projects: number;
  pending_reviews: number;
  todays_tasks: number;
  ai_jobs_running: number;
  published_videos: number;
  storage_bytes: number;
  publishing_queue?: number;
  ai_jobs_queued?: number;
  revenue_mrr?: number;
  total_views?: number;
}

export interface PipelineStageCount {
  stage: string;
  count: number;
}

export interface MonthlyMetric {
  month: string;
  revenue: number;
  views: number;
  productions: number;
}

export interface StatusCount {
  label: string;
  count: number;
}

export interface ActivityLog {
  id: number;
  action: string;
  entity_type: string | null;
  entity_id?: number | null;
  created_at: string;
}

export interface Approval {
  id: number;
  entity_type: string;
  status: string;
  created_at: string;
}

export interface StudioTask {
  id: number;
  title: string;
  description?: string | null;
  status: string;
  priority: string;
  due_date: string | null;
  project_id?: number | null;
}

export interface Notification {
  id: number;
  notification_type: string;
  title: string;
  body: string | null;
  is_read: boolean;
  created_at: string;
}

export interface DashboardData {
  overview: DashboardOverview;
  production_pipeline: PipelineStageCount[];
  monthly_analytics: MonthlyMetric[];
  project_status: StatusCount[];
  recent_projects: Project[];
  recent_activity: ActivityLog[];
  upcoming_deadlines: StudioTask[];
  notifications: Notification[];
  pending_approvals: Approval[];
  todays_tasks: StudioTask[];
}

export interface User {
  id: number;
  email: string;
  full_name: string;
  is_admin: boolean;
}
