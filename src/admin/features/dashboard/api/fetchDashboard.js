import { dashboard, studio, studioPlatform } from '../../../api/adminApi';
import { ACTIVE_PRODUCTIONS } from '../../../../data/studioData';
import { buildDashboardFallback } from '../utils';

export async function fetchDashboard() {
  try {
    const data = await studioPlatform.getDashboard();
    return { ...data, live: true };
  } catch {
    // Platform API unavailable — compose from legacy endpoints + demo data
  }

  const [stats, analytics, revenue, productions, agents] = await Promise.all([
    dashboard.getStats().catch(() => ({})),
    dashboard.getAnalytics().catch(() => ({})),
    dashboard.getRevenue().catch(() => ({})),
    studio.listProductions().catch(() => null),
    studio.getAgents().catch(() => null),
  ]);

  const apiItems = productions?.items?.length ? productions.items : null;
  const items = apiItems || ACTIVE_PRODUCTIONS.map((p) => ({
    id: p.id,
    title: p.title,
    stage: p.stage,
    status: p.status,
    assignee: p.assignee,
    publishing_status: 'unpublished',
  }));

  const fallback = buildDashboardFallback({ stats, analytics, revenue, items, agents });
  return { ...fallback, live: Boolean(apiItems) };
}
