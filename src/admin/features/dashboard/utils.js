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
        views: Math.round((analytics.total_views || 0) / 6),
        productions: Math.max(1, Math.floor(items.length / 6)),
      }))
    : [
        { month: 'Jan', revenue: 4200, views: 12000, productions: 2 },
        { month: 'Feb', revenue: 5100, views: 14500, productions: 3 },
        { month: 'Mar', revenue: 4800, views: 13200, productions: 2 },
        { month: 'Apr', revenue: 6200, views: 16800, productions: 4 },
        { month: 'May', revenue: 5900, views: 15400, productions: 3 },
        { month: 'Jun', revenue: 7100, views: 19200, productions: 4 },
      ];

  const statusCounts = {};
  items.forEach((p) => {
    statusCounts[p.status] = (statusCounts[p.status] || 0) + 1;
  });

  const recentActivity = [
    { id: 1, action: 'Script v3 submitted for review', entity_type: 'script', created_at: new Date(Date.now() - 3600000).toISOString() },
    { id: 2, action: 'Research pack approved', entity_type: 'research', created_at: new Date(Date.now() - 7200000).toISOString() },
    { id: 3, action: 'AI thumbnail batch completed', entity_type: 'thumbnail', created_at: new Date(Date.now() - 86400000).toISOString() },
  ];

  const upcomingDeadlines = [
    { id: 1, title: 'MrBeast script final', priority: 'high', due_date: new Date(Date.now() + 86400000 * 2).toISOString() },
    { id: 2, title: 'Ronaldo edit lock', priority: 'medium', due_date: new Date(Date.now() + 86400000 * 5).toISOString() },
  ];

  const notifications = [
    { id: 1, title: 'Publishing queue: 1 title scheduled', body: null, is_read: false, created_at: new Date().toISOString() },
    { id: 2, title: 'Fact-check flagged 2 claims', body: 'Review before publish.', is_read: true, created_at: new Date(Date.now() - 3600000).toISOString() },
  ];

  return {
    live: false,
    overview: {
      active_projects: items.length || stats.videos || items.length,
      pending_reviews: items.filter((p) => p.status === 'review').length,
      todays_tasks: 3,
      ai_jobs_running: agents?.active_count ?? 6,
      ai_jobs_queued: agents?.queued_count ?? 2,
      published_videos: stats.videos ?? 12,
      storage_bytes: 2.4 * 1024 ** 3,
      publishing_queue: items.filter((p) => normalizeStage(p.stage) === 'publish').length,
      total_views: analytics.total_views ?? 84200,
    },
    production_pipeline: PIPELINE_STAGES.map((stage) => ({ stage, count: stageCounts[stage] || 0 })),
    monthly_analytics: monthly,
    project_status: Object.keys(statusCounts).length
      ? Object.entries(statusCounts).map(([label, count]) => ({ label, count }))
      : [
          { label: 'active', count: 3 },
          { label: 'review', count: 1 },
          { label: 'scheduled', count: 1 },
        ],
    recent_projects: items.slice(0, 8),
    recent_activity: recentActivity,
    upcoming_deadlines: upcomingDeadlines,
    notifications,
    todays_tasks: [],
    pending_approvals: [],
  };
}
