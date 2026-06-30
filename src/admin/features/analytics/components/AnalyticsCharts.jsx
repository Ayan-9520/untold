import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts';
import ChartCard from '../../../components/ChartCard';

const COLORS = ['#D4AF37', '#3B82F6', '#10B981', '#8B5CF6', '#EF4444', '#F59E0B'];
const tooltipStyle = { backgroundColor: '#141414', border: '1px solid #2a2a2a', borderRadius: '8px', fontSize: '12px' };

export function GrowthChart({ data }) {
  return (
    <ChartCard title="Growth" subtitle="Views, revenue & subscribers (30d)">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data || []}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2a2a" opacity={0.3} />
          <XAxis dataKey="date" tick={{ fontSize: 10, fill: '#8a8a8a' }} tickFormatter={(d) => d?.slice(5)} axisLine={false} tickLine={false} />
          <YAxis yAxisId="left" tick={{ fontSize: 10, fill: '#8a8a8a' }} axisLine={false} tickLine={false} />
          <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 10, fill: '#8a8a8a' }} axisLine={false} tickLine={false} />
          <Tooltip contentStyle={tooltipStyle} />
          <Legend wrapperStyle={{ fontSize: '11px' }} />
          <Line yAxisId="left" type="monotone" dataKey="views" stroke="#D4AF37" strokeWidth={2} dot={false} name="Views" />
          <Line yAxisId="right" type="monotone" dataKey="subscribers" stroke="#3B82F6" strokeWidth={2} dot={false} name="Subscribers" />
        </LineChart>
      </ResponsiveContainer>
    </ChartCard>
  );
}

export function BreakdownChart({ title, data }) {
  return (
    <ChartCard title={title}>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie data={data || []} cx="50%" cy="50%" innerRadius={50} outerRadius={90} dataKey="pct" nameKey="label" paddingAngle={2}>
            {(data || []).map((_, i) => (
              <Cell key={i} fill={COLORS[i % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip contentStyle={tooltipStyle} formatter={(v) => `${v}%`} />
          <Legend wrapperStyle={{ fontSize: '10px' }} />
        </PieChart>
      </ResponsiveContainer>
    </ChartCard>
  );
}

export function TopVideosChart({ videos }) {
  const data = (videos || []).slice(0, 6).map((v) => ({ name: v.title?.slice(0, 20), views: v.views }));
  return (
    <ChartCard title="Top Videos" subtitle="By views">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} layout="vertical">
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2a2a" opacity={0.3} />
          <XAxis type="number" tick={{ fontSize: 10, fill: '#8a8a8a' }} axisLine={false} tickLine={false} />
          <YAxis type="category" dataKey="name" width={100} tick={{ fontSize: 9, fill: '#8a8a8a' }} axisLine={false} tickLine={false} />
          <Tooltip contentStyle={tooltipStyle} />
          <Bar dataKey="views" fill="#D4AF37" radius={[0, 4, 4, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </ChartCard>
  );
}

export function RealtimePanel({ realtime }) {
  if (!realtime) return null;
  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
      {[
        { label: 'Active viewers', value: realtime.active_viewers, pulse: true },
        { label: 'Views (1h)', value: realtime.views_last_hour?.toLocaleString() },
        { label: 'Plays (1h)', value: realtime.plays_last_hour?.toLocaleString() },
        { label: 'Revenue today', value: `$${realtime.revenue_today?.toLocaleString()}` },
      ].map((s) => (
        <div key={s.label} className="ai-stat-card relative">
          {s.pulse && <span className="absolute top-2 right-2 w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />}
          <p className="text-lg font-bold text-untold-gold">{s.value}</p>
          <p className="text-[10px] dark:text-untold-muted mt-1">{s.label}</p>
        </div>
      ))}
    </div>
  );
}
