import { motion } from 'framer-motion';

import {

  Briefcase,

  CheckSquare,

  Cpu,

  HardDrive,

  Video,

  ClipboardCheck,

  Activity,

  CalendarClock,

  Bell,

} from 'lucide-react';

import { useDashboard } from '@/features/dashboard/hooks/useDashboard';

import StatCard from '@/features/dashboard/StatCard';

import DashboardSection, { ChartPanel } from '@/features/dashboard/DashboardSection';

import ProductionPipelineChart from '@/features/dashboard/ProductionPipelineChart';

import MonthlyAnalyticsChart from '@/features/dashboard/MonthlyAnalyticsChart';

import ProjectStatusChart from '@/features/dashboard/ProjectStatusChart';

import RecentProductionsList from '@/features/dashboard/RecentProductionsList';

import ActivityFeed from '@/features/dashboard/ActivityFeed';

import DeadlinesList from '@/features/dashboard/DeadlinesList';

import NotificationsList from '@/features/dashboard/NotificationsList';

import { DashboardError, DashboardSkeleton } from '@/features/dashboard/DashboardSkeleton';

import { formatBytes } from '@/features/dashboard/utils';



export default function DashboardPage() {

  const { data, isLoading, isError, refetch, isFetching } = useDashboard();



  if (isLoading) return <DashboardSkeleton />;

  if (isError || !data) return <DashboardError onRetry={() => refetch()} />;



  const { overview } = data;

  const unreadNotifications = (data.notifications || []).filter((n) => !n.is_read).length;



  return (

    <motion.div

      initial={{ opacity: 0, y: 8 }}

      animate={{ opacity: 1, y: 0 }}

      transition={{ duration: 0.35 }}

      className="space-y-8"

    >

      <header className="flex items-start justify-between gap-4">

        <div>

          <p className="text-xs font-bold tracking-[0.25em] text-studio-gold uppercase">Production OS</p>

          <h1 className="text-3xl font-bold text-white mt-1">Dashboard</h1>

          <p className="text-sm text-studio-muted mt-1 max-w-2xl">

            Active productions, pipeline health, AI jobs, publishing, and team activity at a glance.

          </p>

        </div>

        {isFetching && !isLoading && (

          <span className="text-[10px] uppercase tracking-wider text-studio-muted">Refreshing…</span>

        )}

      </header>



      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">

        <StatCard label="Active Projects" value={overview.active_projects} icon={Briefcase} />

        <StatCard label="Pending Reviews" value={overview.pending_reviews} icon={ClipboardCheck} />

        <StatCard label="Today's Tasks" value={overview.todays_tasks} icon={CheckSquare} />

        <StatCard

          label="AI Jobs Running"

          value={overview.ai_jobs_running}

          icon={Cpu}

          hint={overview.ai_jobs_queued ? `${overview.ai_jobs_queued} queued` : undefined}

        />

        <StatCard label="Published Videos" value={overview.published_videos} icon={Video} />

        <StatCard label="Storage Usage" value={formatBytes(overview.storage_bytes)} icon={HardDrive} />

        <StatCard

          label="Recent Activity"

          value={(data.recent_activity || []).length}

          icon={Activity}

          hint="Audit events"

        />

        <StatCard

          label="Upcoming Deadlines"

          value={(data.upcoming_deadlines || []).length}

          icon={CalendarClock}

          hint="Next 14 days"

        />

        <StatCard

          label="Notifications"

          value={unreadNotifications}

          icon={Bell}

          hint={unreadNotifications ? 'Unread' : 'All caught up'}

        />

      </div>



      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">

        <ChartPanel title="Production Pipeline" subtitle="Projects by stage">

          <ProductionPipelineChart data={data.production_pipeline} />

        </ChartPanel>

        <ChartPanel title="Monthly Analytics" subtitle="Revenue & views (6 months)">

          <MonthlyAnalyticsChart data={data.monthly_analytics} />

        </ChartPanel>

        <ChartPanel title="Project Status" subtitle="Distribution by status" className="lg:col-span-2 xl:col-span-1">

          <ProjectStatusChart data={data.project_status} />

        </ChartPanel>

      </div>



      <DashboardSection

        title="Recent Productions"

        subtitle="Latest active projects in the pipeline"

        actionLabel="View all →"

        actionTo="/projects"

      >

        <RecentProductionsList projects={data.recent_projects} />

      </DashboardSection>



      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">

        <DashboardSection title="Recent Activity" subtitle="Studio audit log">

          <ActivityFeed items={data.recent_activity} />

        </DashboardSection>



        <DashboardSection

          title="Upcoming Deadlines"

          subtitle="Next 14 days"

          actionLabel="Tasks →"

          actionTo="/tasks"

        >

          <DeadlinesList items={data.upcoming_deadlines} />

        </DashboardSection>



        <DashboardSection

          title="Notifications"

          subtitle="Alerts & updates"

          actionLabel="View all →"

          actionTo="/notifications"

        >

          <NotificationsList items={data.notifications} />

        </DashboardSection>

      </div>

    </motion.div>

  );

}

