import { useAnalyticsOverview, useAnalyticsRealtime } from '../hooks/useAnalytics';
import { GrowthChart, BreakdownChart, TopVideosChart, RealtimePanel } from './AnalyticsCharts';
import StudioPageHeader from '../../../components/StudioPageHeader';
import PipelineBar from '../../../components/PipelineBar';
import StudioLiveBadge from '../../../components/StudioLiveBadge';
import StatCard from '../../../components/StatCard';
import { DownloadIcon, EyeIcon, TrendingUpIcon, DollarSignIcon } from '../../../components/AdminIcons';

async function downloadExport(path, filename) {
  const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
  const token = localStorage.getItem('untold-admin-token');
  const res = await fetch(`${API_BASE}${path}`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
}

export default function AnalyticsDashboard() {
  const { data, isLoading, isError } = useAnalyticsOverview();
  const { data: realtime } = useAnalyticsRealtime();

  if (isLoading) return <div className="h-96 skeleton rounded-xl" />;

  return (
    <div className="space-y-6 animate-fade-in">
      <StudioPageHeader
        section="Analytics"
        title="Viewer Analytics"
        description="Views, watch time, CTR, revenue, traffic & growth — realtime dashboard."
      >
        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => downloadExport('/studio/platform/analytics/export/csv', 'untold-analytics.csv')}
            className="flex items-center gap-2 px-3 py-2 rounded-lg text-xs border dark:border-white/10 hover:text-untold-gold"
          >
            <DownloadIcon className="w-3.5 h-3.5" /> CSV
          </button>
          <button
            type="button"
            onClick={() => downloadExport('/studio/platform/analytics/export/pdf', 'untold-analytics-report.txt')}
            className="flex items-center gap-2 px-3 py-2 rounded-lg text-xs border dark:border-white/10 hover:text-untold-gold"
          >
            <DownloadIcon className="w-3.5 h-3.5" /> PDF
          </button>
          <StudioLiveBadge live={!isError} />
        </div>
      </StudioPageHeader>
      <PipelineBar activeStep="analytics" />

      <RealtimePanel realtime={realtime} />

      {data && (
        <>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
            <StatCard title="Views" value={data.views?.toLocaleString()} icon={EyeIcon} accent="gold" />
            <StatCard title="Watch time" value={`${data.watch_time_hours?.toLocaleString()}h`} accent="blue" />
            <StatCard title="CTR" value={`${data.ctr}%`} accent="green" />
            <StatCard title="Revenue" value={`$${Math.round(data.revenue)?.toLocaleString()}`} icon={DollarSignIcon} accent="gold" />
            <StatCard title="Subscribers" value={data.subscribers?.toLocaleString()} icon={TrendingUpIcon} accent="blue" />
          </div>

          <p className="text-xs dark:text-untold-muted">
            Views +{data.views_growth_pct}% · Subscribers +{data.subscriber_growth_pct}% vs prior period
          </p>

          <GrowthChart data={data.growth} />

          <div className="grid xl:grid-cols-3 gap-4">
            <BreakdownChart title="Traffic sources" data={data.traffic_sources} />
            <BreakdownChart title="Countries" data={data.countries} />
            <BreakdownChart title="Devices" data={data.devices} />
          </div>

          <div className="grid xl:grid-cols-2 gap-4">
            <TopVideosChart videos={data.top_videos} />
            <div className="rounded-xl border dark:border-white/10 overflow-hidden">
              <div className="px-5 py-4 border-b dark:border-white/10">
                <h3 className="text-sm font-semibold dark:text-white">Top creators</h3>
              </div>
              <div className="divide-y dark:divide-white/5">
                {data.top_creators?.map((c, i) => (
                  <div key={c.name} className="flex justify-between px-5 py-3 text-sm">
                    <span><span className="text-untold-gold mr-2">#{i + 1}</span>{c.name}</span>
                    <span className="dark:text-untold-muted">{c.total_views?.toLocaleString()} views · {c.projects} projects</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="rounded-xl border dark:border-white/10 overflow-hidden">
            <div className="px-5 py-4 border-b dark:border-white/10">
              <h3 className="text-sm font-semibold dark:text-white">Top videos detail</h3>
            </div>
            <table className="w-full text-xs">
              <thead>
                <tr className="dark:text-untold-muted border-b dark:border-white/10">
                  <th className="text-left py-2 px-5">Title</th>
                  <th className="text-right py-2 px-3">Views</th>
                  <th className="text-right py-2 px-3">Watch time</th>
                  <th className="text-right py-2 px-5">CTR</th>
                </tr>
              </thead>
              <tbody>
                {data.top_videos?.map((v) => (
                  <tr key={v.id} className="border-b dark:border-white/5">
                    <td className="py-2.5 px-5 dark:text-white">{v.title}</td>
                    <td className="py-2.5 px-3 text-right dark:text-untold-muted">{v.views?.toLocaleString()}</td>
                    <td className="py-2.5 px-3 text-right dark:text-untold-muted">{v.watch_time_hours}h</td>
                    <td className="py-2.5 px-5 text-right text-untold-gold">{v.ctr}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}
