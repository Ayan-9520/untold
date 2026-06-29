import { useState, useEffect } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend,
} from 'recharts';
import ChartCard from '../components/ChartCard';
import StatCard from '../components/StatCard';
import { DollarSignIcon, TrendingUpIcon, DownloadIcon } from '../components/AdminIcons';
import { dashboard } from '../api/adminApi';
import { REVENUE_STREAMS } from '../../data/revenueStrategy';

const COLORS = ['#6B7280', '#D4AF37', '#8B5CF6'];
const tooltipStyle = { backgroundColor: '#141414', border: '1px solid #2a2a2a', borderRadius: '8px', fontSize: '12px' };

export default function RevenuePage() {
  const [revenue, setRevenue] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    dashboard.getRevenue()
      .then(setRevenue)
      .finally(() => setLoading(false));
  }, []);

  const exportReport = () => {
    const blob = new Blob([JSON.stringify(revenue, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'untold-revenue-report.json';
    a.click();
  };

  if (loading) return <div className="h-96 rounded-xl skeleton" />;

  const planData = Object.entries(revenue?.revenue_by_plan || {}).map(([name, value]) => ({
    name: name.charAt(0).toUpperCase() + name.slice(1),
    value,
  }));

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold dark:text-untold-white light:text-black">Revenue</h1>
          <p className="text-sm dark:text-untold-muted light:text-gray-500 mt-1">Subscription revenue and growth</p>
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

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <StatCard title="MRR" value={`$${revenue?.mrr?.toLocaleString()}`} change={revenue?.growth_rate} icon={DollarSignIcon} accent="gold" />
        <StatCard title="ARR" value={`$${revenue?.arr?.toLocaleString()}`} icon={TrendingUpIcon} accent="green" />
        <StatCard title="Total Revenue" value={`$${revenue?.total_revenue?.toLocaleString()}`} accent="blue" />
        <StatCard title="Active Subs" value={revenue?.active_subscriptions} accent="purple" />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        <ChartCard title="Monthly Revenue" subtitle="Last 6 months">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={revenue?.monthly_revenue || []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2a2a2a" opacity={0.3} />
              <XAxis dataKey="month" tick={{ fontSize: 11, fill: '#8a8a8a' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: '#8a8a8a' }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={tooltipStyle} formatter={(v) => [`$${v}`, 'Revenue']} />
              <Bar dataKey="revenue" fill="#D4AF37" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Revenue by Plan" subtitle="Active subscription breakdown">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={planData} cx="50%" cy="50%" innerRadius={55} outerRadius={95} dataKey="value" paddingAngle={4}>
                {planData.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip contentStyle={tooltipStyle} formatter={(v) => [`$${v}`, 'Revenue']} />
              <Legend wrapperStyle={{ fontSize: '11px' }} />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      <div>
        <h2 className="text-lg font-semibold dark:text-untold-white light:text-black mb-4">Monetization Streams</h2>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {REVENUE_STREAMS.map((stream) => (
            <div key={stream.id} className="rounded-xl p-4 border dark:border-white/10 light:border-gray-200">
              <span className="text-2xl">{stream.icon}</span>
              <h3 className="mt-2 font-semibold dark:text-untold-white light:text-black">{stream.label}</h3>
              <p className="text-xs dark:text-untold-muted light:text-gray-500 mt-1">{stream.description}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
