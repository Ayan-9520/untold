import { ChartPanel } from './DashboardSection';

export function DashboardSkeleton() {
  return (
    <div className="space-y-8 animate-pulse">
      <div className="h-16 w-72 rounded-lg skeleton" />
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {Array.from({ length: 9 }).map((_, i) => (
          <div key={i} className="h-28 rounded-xl skeleton" />
        ))}
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="h-72 rounded-xl skeleton" />
        ))}
      </div>
      <div className="h-48 rounded-xl skeleton" />
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="h-56 rounded-xl skeleton" />
        ))}
      </div>
    </div>
  );
}

export function DashboardError({ onRetry }) {
  return (
    <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-8 text-center max-w-md mx-auto mt-12">
      <p className="text-red-400 font-medium">Failed to load dashboard</p>
      <p className="text-sm dark:text-untold-muted light:text-gray-500 mt-2">
        Ensure the API is running and you are signed in.
      </p>
      <button
        type="button"
        onClick={onRetry}
        className="mt-4 px-4 py-2 rounded-lg bg-untold-gold text-black text-sm font-semibold"
      >
        Retry
      </button>
    </div>
  );
}

export function ChartPanelSkeleton({ title }) {
  return (
    <ChartPanel title={title}>
      <div className="h-full min-h-[200px] rounded-lg skeleton" />
    </ChartPanel>
  );
}
