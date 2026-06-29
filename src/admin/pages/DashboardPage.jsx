import { useState, useEffect } from 'react';
import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts';
import StatCard from '../components/StatCard';
import ChartCard from '../components/ChartCard';
import { UsersIcon, FilmIcon, DollarSignIcon, EyeIcon } from '../components/AdminIcons';
import { dashboard } from '../api/adminApi';

const tooltipStyle = {
  backgroundColor: '#141414',
  border: '1px solid #2a2a2a',
  borderRadius: '8px',
  fontSize: '12px',
};

export default function DashboardPage() {
  const [stats, setStats] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [revenue, setRevenue] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    Promise.all([
      dashboard.getStats(),
      dashboard.getAnalytics(),
      dashboard.getRevenue(),
    ])
      .then(([s, a, r]) => {
        setStats(s);
        setAnalytics(a);
        setRevenue(r);
      })
      .catch((err) => setError(err.response?.data?.detail || 'Failed to load dashboard'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="h-32 rounded-xl skeleton" />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-xl p-8 text-center dark:bg-untold-surface light:bg-white border dark:border-white/5">
        <p className="text-red-400">{error}</p>
        <p className="text-xs dark:text-untold-muted light:text-gray-500 mt-2">
          Ensure the FastAPI backend is running at {import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'}
        </p>
      </div>
    );
  }

  const engagementRate = analytics?.total_views
    ? Math.round((analytics.events_last_7d / Math.max(analytics.total_views, 1)) * 100)
    : 0;

  const viewsData = analytics?.top_videos?.map((v) => ({
    name: v.title?.slice(0, 15) + (v.title?.length > 15 ? '…' : ''),
    views: v.views,
  })) || [];

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold dark:text-untold-white light:text-black">Dashboard</h1>
        <p className="text-sm dark:text-untold-muted light:text-gray-500 mt-1">
          Platform overview and key metrics
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <StatCard title="Total Users" value={stats?.users?.toLocaleString() ?? '—'} change={8.2} icon={UsersIcon} accent="blue" />
        <StatCard title="Total Videos" value={stats?.videos?.toLocaleString() ?? '—'} change={4.1} icon={FilmIcon} accent="gold" />
        <StatCard title="Revenue" value={`$${revenue?.mrr?.toLocaleString() ?? '0'}`} change={revenue?.growth_rate} icon={DollarSignIcon} accent="green" />
        <StatCard title="Engagement" value={`${engagementRate}%`} change={2.8} icon={EyeIcon} accent="purple" />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        <ChartCard title="Revenue Trend" subtitle="Monthly recurring revenue">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={revenue?.monthly_revenue || []}>
              <defs>
                <linearGradient id="goldGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#D4AF37" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#D4AF37" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#2a2a2a" opacity={0.3} />
              <XAxis dataKey="month" tick={{ fontSize: 11, fill: '#8a8a8a' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: '#8a8a8a' }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={tooltipStyle} />
              <Area type="monotone" dataKey="revenue" stroke="#D4AF37" fill="url(#goldGrad)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Top Videos" subtitle="By view count">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={viewsData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2a2a2a" opacity={0.3} />
              <XAxis dataKey="name" tick={{ fontSize: 10, fill: '#8a8a8a' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: '#8a8a8a' }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={tooltipStyle} />
              <Bar dataKey="views" fill="#D4AF37" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {[
          { label: 'Categories', value: stats?.categories },
          { label: 'Watchlist Items', value: stats?.watchlist_items },
          { label: 'Subscriptions', value: stats?.subscriptions },
          { label: 'Events (24h)', value: analytics?.events_last_24h },
        ].map((item) => (
          <div key={item.label} className="rounded-xl p-4 dark:bg-untold-surface light:bg-white border dark:border-white/5 light:border-gray-200 text-center">
            <p className="text-xl font-bold text-untold-gold">{item.value ?? '—'}</p>
            <p className="text-xs dark:text-untold-muted light:text-gray-500 mt-1">{item.label}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
