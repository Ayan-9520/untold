export function formatBytes(bytes) {
  if (!bytes) return '0 B';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 ** 2) return `${(bytes / 1024).toFixed(1)} KB`;
  if (bytes < 1024 ** 3) return `${(bytes / 1024 ** 2).toFixed(1)} MB`;
  return `${(bytes / 1024 ** 3).toFixed(2)} GB`;
}

export function formatRelativeTime(iso) {
  const diff = Math.floor((Date.now() - new Date(iso).getTime()) / 1000);
  if (diff < 60) return 'Just now';
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  if (diff < 604800) return `${Math.floor(diff / 86400)}d ago`;
  return new Date(iso).toLocaleDateString();
}

export function formatStage(stage) {
  return (stage || '').replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
}

export function formatDueDate(iso) {
  if (!iso) return 'No date';
  const due = new Date(iso);
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  due.setHours(0, 0, 0, 0);
  const diff = Math.round((due - today) / 86400000);
  if (diff === 0) return 'Today';
  if (diff === 1) return 'Tomorrow';
  if (diff < 0) return `${Math.abs(diff)}d overdue`;
  return due.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
}

const PIPELINE_STAGES = ['research', 'script', 'storyboard', 'image', 'voice', 'video', 'seo', 'publisher', 'editing', 'review', 'completed'];

export function normalizeStage(stage) {
  if (stage === 'edit' || stage === 'video') return 'editing';
  if (stage === 'publish' || stage === 'publishing') return stage === 'publish' ? 'publishing' : stage;
  return stage;
}

export function buildDashboardFallback({ stats = {}, analytics = {}, revenue = {}, items = [], agents = null }) {
  const stageCounts = {};
  items.forEach((p) => {
    const stage = normalizeStage(p.stage);
    stageCounts[stage] = (stageCounts[stage] || 0) + 1;
  });

  const monthly = revenue.monthly_revenue?.length
    ? revenue.monthly_revenue.map((m) => ({
        month: m.month,
        revenue: m.revenue,
        views: Math.round((analytics.total_views || 0) / Math.max(revenue.monthly_revenue.length, 1)),
        productions: Math.max(0, Math.floor(items.length / Math.max(revenue.monthly_revenue.length, 1))),
      }))
    : [];

  const statusCounts = {};
  items.forEach((p) => {
    statusCounts[p.status] = (statusCounts[p.status] || 0) + 1;
  });

  return {
    live: false,
    overview: {
      active_projects: items.length,
      pending_reviews: items.filter((p) => p.status === 'review').length,
      todays_tasks: 0,
      ai_jobs_running: agents?.active_count ?? 0,
      ai_jobs_queued: agents?.queued_count ?? 0,
      published_videos: stats.videos ?? 0,
      storage_bytes: 0,
      publishing_queue: items.filter((p) => normalizeStage(p.stage) === 'publish').length,
      total_views: analytics.total_views ?? 0,
    },
    production_pipeline: PIPELINE_STAGES.map((stage) => ({ stage, count: stageCounts[stage] || 0 })),
    monthly_analytics: monthly,
    project_status: Object.entries(statusCounts).map(([label, count]) => ({ label, count })),
    recent_projects: items.slice(0, 8),
    recent_activity: [],
    upcoming_deadlines: [],
    notifications: [],
    todays_tasks: [],
    pending_approvals: [],
  };
}
