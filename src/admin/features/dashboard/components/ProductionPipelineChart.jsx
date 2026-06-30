import {
  Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from 'recharts';
import { formatStage } from '../utils';

const TOOLTIP = {
  backgroundColor: '#141414',
  border: '1px solid #2a2a2a',
  borderRadius: '8px',
  fontSize: '12px',
};

export default function ProductionPipelineChart({ data = [] }) {
  const chartData = data.map((d) => ({
    stage: formatStage(d.stage),
    count: d.count,
  }));

  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={chartData} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#2a2a2a" vertical={false} opacity={0.3} />
        <XAxis
          dataKey="stage"
          tick={{ fill: '#8a8a8a', fontSize: 10 }}
          axisLine={false}
          tickLine={false}
          interval={0}
          angle={-25}
          textAnchor="end"
          height={50}
        />
        <YAxis tick={{ fill: '#8a8a8a', fontSize: 11 }} axisLine={false} tickLine={false} allowDecimals={false} />
        <Tooltip contentStyle={TOOLTIP} cursor={{ fill: 'rgba(212, 175, 55, 0.08)' }} />
        <Bar dataKey="count" fill="#D4AF37" radius={[4, 4, 0, 0]} maxBarSize={40} />
      </BarChart>
    </ResponsiveContainer>
  );
}
