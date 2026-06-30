import StudioPageHeader from '../components/StudioPageHeader';
import {
  FilmIcon,
  UsersIcon,
  BookIcon,
  GlobeIcon,
  BellIcon,
  TrendingUpIcon,
} from '../components/AdminIcons';
import { studioPath } from '../../config/ecosystem';
import {
  useDashboard,
  StatCard,
  DashboardSection,
  ChartPanel,
  ProductionPipelineChart,
  MonthlyAnalyticsChart,
  ProjectStatusChart,
  RecentProductionsList,
  ActivityFeed,
  DeadlinesList,
  NotificationsList,
  DashboardSkeleton,
  DashboardError,
  formatBytes,
} from '../features/dashboard';

function StorageIcon(props) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className={props.className}>
      <ellipse cx="12" cy="5" rx="9" ry="3" />
      <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5" />
      <path d="M3 12c0 1.66 4 3 9 3s9-1.34 9-3" />
    </svg>
  );
}

export default function DashboardPage() {
  const { data, isLoading, isError, refetch, isFetching } = useDashboard();

  if (isLoading) return <DashboardSkeleton />;
  if (isError || !data) return <DashboardError onRetry={() => refetch()} />;

  const { overview } = data;
  const unreadNotifications = (data.notifications || []).filter((n) => !n.is_read).length;

  return (
    <div className="space-y-8 animate-fade-in">
      {!data.live && (
        <div className="rounded-lg border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-sm text-amber-200/90">
          Demo pipeline data — rebuild Docker for full live Studio API sync.
        </div>
      )}

      <StudioPageHeader
        title="Production Dashboard"
        description="Active projects, pipeline, AI jobs, publishing, and team activity"
      >
        {isFetching && !isLoading && (
          <span className="text-[10px] uppercase tracking-wider text-untold-muted">Refreshing…</span>
        )}
        {data.live && (
          <span className="studio-live-badge">● Live</span>
        )}
      </StudioPageHeader>

      {/* Dashboard cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        <StatCard label="Active Projects" value={overview.active_projects} icon={FilmIcon} accent="gold" />
        <StatCard label="Pending Reviews" value={overview.pending_reviews} icon={UsersIcon} accent="purple" />
        <StatCard label="Today's Tasks" value={overview.todays_tasks} icon={BookIcon} accent="blue" />
        <StatCard
          label="AI Jobs Running"
          value={overview.ai_jobs_running}
          icon={GlobeIcon}
          accent="green"
          hint={overview.ai_jobs_queued ? `${overview.ai_jobs_queued} queued` : undefined}
        />
        <StatCard label="Published Videos" value={overview.published_videos} icon={FilmIcon} accent="gold" />
        <StatCard label="Storage Usage" value={formatBytes(overview.storage_bytes)} icon={StorageIcon} accent="blue" />
        <StatCard
          label="Recent Activity"
          value={(data.recent_activity || []).length}
          icon={TrendingUpIcon}
          accent="amber"
          hint="Audit events"
        />
        <StatCard
          label="Upcoming Deadlines"
          value={(data.upcoming_deadlines || []).length}
          icon={BookIcon}
          accent="purple"
          hint="Next 14 days"
        />
        <StatCard
          label="Notifications"
          value={unreadNotifications}
          icon={BellIcon}
          accent="gold"
          hint={unreadNotifications ? 'Unread' : 'All caught up'}
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
        <ChartPanel title="Production Pipeline" subtitle="Projects by stage">
          <ProductionPipelineChart data={data.production_pipeline} />
        </ChartPanel>
        <ChartPanel title="Monthly Analytics" subtitle="Revenue & views">
          <MonthlyAnalyticsChart data={data.monthly_analytics} />
        </ChartPanel>
        <ChartPanel title="Project Status" subtitle="By status" className="lg:col-span-2 xl:col-span-1">
          <ProjectStatusChart data={data.project_status} />
        </ChartPanel>
      </div>

      {/* Recent productions */}
      <DashboardSection
        title="Recent Productions"
        subtitle="Latest in pipeline"
        actionTo={studioPath('research')}
        actionLabel="View all →"
      >
        <RecentProductionsList projects={data.recent_projects} />
      </DashboardSection>

      {/* Activity, deadlines, notifications */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        <DashboardSection title="Recent Activity" subtitle="Studio audit log">
          <ActivityFeed items={data.recent_activity} />
        </DashboardSection>

        <DashboardSection
          title="Upcoming Deadlines"
          subtitle="Next 14 days"
          actionTo={studioPath('scripts')}
          actionLabel="Tasks →"
        >
          <DeadlinesList items={data.upcoming_deadlines} />
        </DashboardSection>

        <DashboardSection
          title="Notifications"
          subtitle="Alerts & updates"
          actionTo={studioPath('notifications')}
          actionLabel="View all →"
        >
          <NotificationsList items={data.notifications} />
        </DashboardSection>
      </div>
    </div>
  );
}
