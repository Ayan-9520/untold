import { STAGE_LABELS, STAGE_COLORS } from '../constants';

export default function StageBadge({ stage, className = '' }) {
  const label = STAGE_LABELS[stage] || stage;
  const colors = STAGE_COLORS[stage] || 'bg-white/10 text-untold-muted border-white/10';
  return (
    <span className={`inline-flex text-[10px] uppercase tracking-wider px-2 py-0.5 rounded-full border ${colors} ${className}`}>
      {label}
    </span>
  );
}
