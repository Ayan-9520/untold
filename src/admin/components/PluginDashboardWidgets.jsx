import { useEffect, useState } from 'react';
import { usePluginHooks } from '../../plugin-sdk';

/**
 * Renders optional dashboard widgets contributed by installed frontend plugins.
 */
export default function PluginDashboardWidgets() {
  const runDashboardWidgets = usePluginHooks('dashboard.widgets');
  const [widgets, setWidgets] = useState([]);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const result = await runDashboardWidgets({});
        if (!cancelled) setWidgets(result?.widgets || []);
      } catch {
        if (!cancelled) setWidgets([]);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [runDashboardWidgets]);

  if (!widgets.length) return null;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {widgets.map((w) => (
        <div key={w.id} className="studio-card p-4">
          <div className="text-[10px] uppercase tracking-wider dark:text-untold-muted">{w.title}</div>
          {w.type === 'list' && Array.isArray(w.items) ? (
            <ul className="mt-2 text-xs space-y-1 dark:text-untold-muted">
              {w.items.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          ) : (
            <div className="text-2xl font-semibold text-untold-gold mt-1">{w.value}</div>
          )}
        </div>
      ))}
    </div>
  );
}
