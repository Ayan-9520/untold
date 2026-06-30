import { ChartPanel } from './DashboardSection';

export function DashboardSkeleton() {
  return (
    <div className="space-y-8 animate-pulse">
      <div className="h-16 w-64 rounded-lg bg-studio-card" />
      <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-4">
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="h-24 rounded-xl bg-studio-card" />
        ))}
      </div>
      <div className="grid lg:grid-cols-2 gap-6">
        <div className="h-72 rounded-xl bg-studio-card" />
        <div className="h-72 rounded-xl bg-studio-card" />
      </div>
    </div>
  );
}

export function DashboardError({ onRetry }: { onRetry: () => void }) {
  return (
    <div className="studio-glass rounded-xl p-8 text-center max-w-md mx-auto mt-12">
      <p className="text-white font-medium">Failed to load dashboard</p>
      <p className="text-sm text-studio-muted mt-2">Ensure the API is running and you are signed in.</p>
      <button
        type="button"
        onClick={onRetry}
        className="mt-4 px-4 py-2 rounded-lg bg-studio-gold text-black text-sm font-semibold"
      >
        Retry
      </button>
    </div>
  );
}

export function StatsGridSkeleton() {
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-4">
      {Array.from({ length: 8 }).map((_, i) => (
        <div key={i} className="h-24 rounded-xl bg-studio-card animate-pulse" />
      ))}
    </div>
  );
}

export function ChartSkeleton() {
  return <div className="h-[220px] rounded-lg bg-studio-surface/50 animate-pulse" />;
}

export function ChartPanelSkeleton({ title }: { title: string }) {
  return (
    <ChartPanel title={title}>
      <ChartSkeleton />
    </ChartPanel>
  );
}
