import { useState, useEffect } from 'react';
import {
  PieChart, Pie, Cell, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts';
import ChartCard from '../components/ChartCard';
import StatCard from '../components/StatCard';
import { DownloadIcon, EyeIcon, TrendingUpIcon } from '../components/AdminIcons';
import { dashboard } from '../api/adminApi';

const COLORS = ['#D4AF37', '#3B82F6', '#10B981', '#8B5CF6', '#EF4444', '#F59E0B'];
const tooltipStyle = { backgroundColor: '#141414', border: '1px solid #2a2a2a', borderRadius: '8px', fontSize: '12px' };

export default function AnalyticsPage() {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    dashboard.getAnalytics()
      .then(setAnalytics)
      .finally(() => setLoading(false));
  }, []);

  const exportReport = () => {
    const report = JSON.stringify(analytics, null, 2);
    const blob = new Blob([report], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'untold-analytics-report.json';
    a.click();
  };

  if (loading) return <div className="h-96 rounded-xl skeleton" />;

  const eventData = Object.entries(analytics?.events_by_type || {}).map(([name, value]) => ({
    name: name.replace(/_/g, ' '),
    value,
  }));

  const engagementData = [
    { period: '24h', events: analytics?.events_last_24h || 0 },
    { period: '7d', events: analytics?.events_last_7d || 0 },
    { period: 'Views', events: analytics?.total_views || 0 },
    { period: 'Watchlist', events: analytics?.total_watchlist_items || 0 },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold dark:text-untold-white light:text-black">Analytics</h1>
          <p className="text-sm dark:text-untold-muted light:text-gray-500 mt-1">Platform engagement and event tracking</p>
        </div>
        <button
          onClick={exportReport}
          className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium
            dark:bg-white/5 light:bg-white border dark:border-white/10 light:border-gray-200
            hover:text-untold-gold transition-colors"
        >
          <DownloadIcon className="w-4 h-4" />
          Export Report
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <StatCard title="Total Views" value={analytics?.total_views?.toLocaleString()} icon={EyeIcon} accent="gold" />
        <StatCard title="Events (7d)" value={analytics?.events_last_7d?.toLocaleString()} icon={TrendingUpIcon} accent="blue" />
        <StatCard title="Watchlist Adds" value={analytics?.total_watchlist_items?.toLocaleString()} accent="green" />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        <ChartCard title="Events by Type" subtitle="Distribution of platform events">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={eventData} cx="50%" cy="50%" innerRadius={60} outerRadius={100} dataKey="value" paddingAngle={3}>
                {eventData.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip contentStyle={tooltipStyle} />
              <Legend wrapperStyle={{ fontSize: '11px' }} />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Engagement Overview" subtitle="Key activity metrics">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={engagementData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2a2a2a" opacity={0.3} />
              <XAxis dataKey="period" tick={{ fontSize: 11, fill: '#8a8a8a' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: '#8a8a8a' }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={tooltipStyle} />
              <Line type="monotone" dataKey="events" stroke="#D4AF37" strokeWidth={2} dot={{ fill: '#D4AF37' }} />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      <div className="rounded-xl dark:bg-untold-surface light:bg-white border dark:border-white/5 light:border-gray-200 overflow-hidden">
        <div className="px-5 py-4 border-b dark:border-white/5 light:border-gray-100">
          <h3 className="text-sm font-semibold dark:text-untold-white light:text-black">Top Performing Videos</h3>
        </div>
        <div className="divide-y dark:divide-white/5 light:divide-gray-50">
          {analytics?.top_videos?.map((video, i) => (
            <div key={video.id} className="flex items-center justify-between px-5 py-3">
              <div className="flex items-center gap-3">
                <span className="text-xs font-bold text-untold-gold w-5">#{i + 1}</span>
                <span className="text-sm dark:text-untold-white light:text-black">{video.title}</span>
              </div>
              <span className="text-sm dark:text-untold-muted light:text-gray-500">{video.views?.toLocaleString()} views</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
