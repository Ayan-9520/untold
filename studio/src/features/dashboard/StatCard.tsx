import type { LucideIcon } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Card } from '@/components/ui/card';

export interface StatCardProps {
  label: string;
  value: string | number;
  icon: LucideIcon;
  hint?: string;
  trend?: 'up' | 'down' | 'neutral';
  className?: string;
}

export default function StatCard({ label, value, icon: Icon, hint, className }: StatCardProps) {
  return (
    <Card className={cn('relative overflow-hidden', className)}>
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-xs font-medium text-studio-muted uppercase tracking-wide">{label}</p>
          <p className="text-2xl font-bold text-studio-gold mt-1.5 tabular-nums">{value}</p>
          {hint && <p className="text-[10px] text-studio-muted mt-1">{hint}</p>}
        </div>
        <div className="shrink-0 p-2.5 rounded-lg bg-studio-gold/10 border border-studio-gold/20">
          <Icon className="w-4 h-4 text-studio-gold" />
        </div>
      </div>
    </Card>
  );
}
