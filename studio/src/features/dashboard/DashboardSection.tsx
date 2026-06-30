import type { ReactNode } from 'react';
import { Link } from 'react-router-dom';
import { cn } from '@/lib/utils';
import { Card, CardTitle } from '@/components/ui/card';

interface DashboardSectionProps {
  title: string;
  subtitle?: string;
  actionLabel?: string;
  actionTo?: string;
  children: ReactNode;
  className?: string;
}

export default function DashboardSection({
  title,
  subtitle,
  actionLabel,
  actionTo,
  children,
  className,
}: DashboardSectionProps) {
  return (
    <section className={cn('space-y-4', className)}>
      <div className="flex items-end justify-between gap-3">
        <div>
          <h2 className="text-sm font-semibold text-white">{title}</h2>
          {subtitle && <p className="text-xs text-studio-muted mt-0.5">{subtitle}</p>}
        </div>
        {actionLabel && actionTo && (
          <Link to={actionTo} className="text-xs font-medium text-studio-gold hover:underline shrink-0">
            {actionLabel}
          </Link>
        )}
      </div>
      <Card className="p-0 overflow-hidden">
        <div className="p-5">{children}</div>
      </Card>
    </section>
  );
}

export function ChartPanel({
  title,
  subtitle,
  children,
  className,
}: {
  title: string;
  subtitle?: string;
  children: ReactNode;
  className?: string;
}) {
  return (
    <Card className={cn('flex flex-col', className)}>
      <div className="mb-4">
        <CardTitle>{title}</CardTitle>
        {subtitle && <p className="text-xs text-studio-muted mt-1">{subtitle}</p>}
      </div>
      <div className="flex-1 min-h-[220px]">{children}</div>
    </Card>
  );
}
