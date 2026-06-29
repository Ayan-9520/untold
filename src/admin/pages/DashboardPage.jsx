import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts';
import StatCard from '../components/StatCard';
import ChartCard from '../components/ChartCard';
import StudioPageHeader from '../components/StudioPageHeader';
import PipelineBar from '../components/PipelineBar';
import { UsersIcon, FilmIcon, DollarSignIcon, EyeIcon } from '../components/AdminIcons';
import { dashboard } from '../api/adminApi';
import { PRODUCTS, studioPath } from '../../config/ecosystem';
import EcosystemFlow from '../../components/ecosystem/EcosystemFlow';
import { useStudioProductions } from '../hooks/useStudioData';
import StudioLiveBadge from '../components/StudioLiveBadge';
import StudioSectionLoader from '../components/StudioSectionLoader';

const MOCK_STATS = { users: 24800, videos: 186, categories: 24, watchlist_items: 9200, subscriptions: 4100 };
const MOCK_REVENUE = {
  mrr: 28400,
  growth_rate: 12.4,
  monthly_revenue: [
    { month: 'Jan', revenue: 18200 },
    { month: 'Feb', revenue: 19800 },
    { month: 'Mar', revenue: 22100 },
    { month: 'Apr', revenue: 24500 },
    { month: 'May', revenue: 26800 },
    { month: 'Jun', revenue: 28400 },
  ],
};
const MOCK_ANALYTICS = {
  total_views: 1240000,
  events_last_7d: 89000,
  events_last_24h: 14200,
  top_videos: [
    { title: 'Virat Kohli', views: 42000 },
    { title: 'MrBeast Rise', views: 38500 },
    { title: 'Steve Jobs', views: 31200 },
    { title: 'Ronaldo', views: 29800 },
  ],
};

const tooltipStyle = {
  backgroundColor: '#141414',
  border: '1px solid #2a2a2a',
  borderRadius: '8px',
  fontSize: '12px',
};

const STAGE_LABELS = {
  research: 'Research',
  script: 'Script',
  edit: 'Editing',
  publishing: 'Publishing',
};

export default function DashboardPage() {
  const [stats, setStats] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [revenue, setRevenue] = useState(null);
  const [loading, setLoading] = useState(true);
  const [usingMock, setUsingMock] = useState(false);
  const { items: productions, loading: productionsLoading, live: productionsLive } = useStudioProductions();

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
      .catch(() => {
        setStats(MOCK_STATS);
        setAnalytics(MOCK_ANALYTICS);
        setRevenue(MOCK_REVENUE);
        setUsingMock(true);
      })
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

  const engagementRate = analytics?.total_views
    ? Math.round((analytics.events_last_7d / Math.max(analytics.total_views, 1)) * 100)
    : 0;

  const viewsData = analytics?.top_videos?.map((v) => ({
    name: v.title?.slice(0, 15) + (v.title?.length > 15 ? '…' : ''),
    views: v.views,
  })) || [];

  return (
    <div className="space-y-6 animate-fade-in">
      <StudioPageHeader
        title="Production Dashboard"
        description={`Produce in Studio → publish to ${PRODUCTS.ORIGINALS.name} → analytics feed back here`}
      />

      {usingMock && (
        <p className="text-xs px-3 py-2 rounded-lg bg-amber-500/10 text-amber-300 border border-amber-500/20">
          Showing sample data — connect backend for live {PRODUCTS.ORIGINALS.name} metrics.
        </p>
      )}

      <PipelineBar />

      <section className="rounded-xl border dark:border-white/10 light:border-gray-200 p-5 dark:bg-untold-card/30">
        <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
          <h2 className="text-sm font-semibold dark:text-white light:text-black">Active productions</h2>
          <div className="flex items-center gap-3">
            <StudioLiveBadge live={productionsLive} />
            <Link to={studioPath('research')} className="text-xs text-untold-gold hover:underline">View all →</Link>
          </div>
        </div>
        {productionsLoading ? (
          <StudioSectionLoader rows={4} />
        ) : (
        <div className="space-y-2">
          {productions.map((p) => (
            <div key={p.id} className="studio-production-row">
              <div className="min-w-0 flex-1">
                <p className="font-medium dark:text-white light:text-black text-sm truncate">{p.title}</p>
                <p className="text-xs dark:text-untold-muted light:text-gray-500 mt-0.5">
                  {STAGE_LABELS[p.stage] || p.stage} · {p.assignee}
                </p>
              </div>
              <span className="text-[10px] uppercase tracking-wider px-2 py-0.5 rounded-full bg-untold-gold/15 text-untold-gold shrink-0">
                {p.status}
              </span>
            </div>
          ))}
        </div>
        )}
      </section>

      <section className="rounded-xl border dark:border-untold-border light:border-gray-200 p-5 dark:bg-untold-card/30">
        <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
          <div>
            <h2 className="text-sm font-bold dark:text-white light:text-black">Ecosystem</h2>
            <p className="text-xs dark:text-untold-muted light:text-gray-500 mt-0.5">
              Phase 1 live · Phase 2 at /ai
            </p>
          </div>
          <Link
            to={studioPath('ecosystem')}
            className="text-xs font-semibold text-untold-gold hover:underline"
          >
            Full ecosystem map →
          </Link>
        </div>
        <EcosystemFlow compact showPhaseBadges />
      </section>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { to: studioPath('research'), label: 'Research' },
          { to: studioPath('scripts'), label: 'Scripts' },
          { to: studioPath('content'), label: 'Publish' },
          { to: studioPath('analytics'), label: 'Analytics' },
        ].map((q) => (
          <Link
            key={q.to}
            to={q.to}
            className="studio-quick-link"
          >
            {q.label} →
          </Link>
        ))}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <StatCard title="OTT Subscribers" value={stats?.subscriptions?.toLocaleString() ?? '—'} change={8.2} icon={UsersIcon} accent="blue" />
        <StatCard title="Published Titles" value={stats?.videos?.toLocaleString() ?? '—'} change={4.1} icon={FilmIcon} accent="gold" />
        <StatCard title="MRR" value={`$${revenue?.mrr?.toLocaleString() ?? '0'}`} change={revenue?.growth_rate} icon={DollarSignIcon} accent="green" />
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

        <ChartCard title="Top on Originals" subtitle="By view count">
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
    </div>
  );
}
