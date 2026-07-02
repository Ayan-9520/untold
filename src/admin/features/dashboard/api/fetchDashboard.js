import { dashboard, studio, studioPlatform } from '../../../api/adminApi';
import { buildDashboardFallback } from '../utils';

export async function fetchDashboard() {
  const data = await studioPlatform.getDashboard();
  return { ...data, live: true };
}

export async function fetchDashboardWithFallback() {
  try {
    return await fetchDashboard();
  } catch {
    const [stats, analytics, revenue, productions, agents] = await Promise.all([
      dashboard.getStats(),
      dashboard.getAnalytics(),
      dashboard.getRevenue(),
      studio.listProductions(),
      studio.getAgents(),
    ]);

    const items = productions?.items?.length ? productions.items : [];
    const fallback = buildDashboardFallback({ stats, analytics, revenue, items, agents });
    return { ...fallback, live: Boolean(productions?.items?.length) };
  }
}
