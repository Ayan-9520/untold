import { useState } from 'react';
import StudioPageHeader from '../components/StudioPageHeader';
import PipelineBar from '../components/PipelineBar';
import StudioLiveBadge from '../components/StudioLiveBadge';
import { useProjects } from '../features/projects/hooks/useProjects';
import {
  usePublishingAgentOverview,
  usePublishingAgentQueue,
  usePublishingAgentHistory,
  usePublishingAgentAnalytics,
  usePublishingAgentWebhooks,
  usePublishingAgentMutations,
} from '../features/publishing-agent/hooks/usePublishingAgent';
import DispatchPanel from '../features/publishing-agent/components/DispatchPanel';
import {
  AgentQueuePanel,
  AgentHistoryPanel,
  AnalyticsPanel,
  WebhooksPanel,
} from '../features/publishing-agent/components/AgentPanels';

const PANELS = ['dispatch', 'queue', 'history', 'analytics', 'webhooks'];
const PANEL_LABELS = {
  dispatch: 'Dispatch',
  queue: 'Queue',
  history: 'History',
  analytics: 'Analytics',
  webhooks: 'Webhooks',
};

export default function PublishingAgentPage() {
  const [panel, setPanel] = useState('dispatch');
  const { data: overview, isError } = usePublishingAgentOverview();
  const { data: queue } = usePublishingAgentQueue();
  const { data: history } = usePublishingAgentHistory();
  const { data: analytics } = usePublishingAgentAnalytics(30);
  const { data: webhooks } = usePublishingAgentWebhooks();
  const { data: projectsData } = useProjects({ limit: 100 });
  const mutations = usePublishingAgentMutations();
  const projects = projectsData?.items || [];

  return (
    <div className="space-y-6">
      <StudioPageHeader
        section="AI Publishing Agent"
        title="Publishing Agent"
        description="Originals · YouTube · Instagram · Facebook · X · Threads · Schedule · Approval · Webhooks"
      >
        <StudioLiveBadge live={!isError} />
      </StudioPageHeader>

      <PipelineBar activeStep="publisher" />

      <div className="grid grid-cols-2 lg:grid-cols-5 gap-3">
        <div className="ai-stat-card text-center">
          <p className="text-2xl font-bold text-untold-gold">{overview?.active_runs ?? 0}</p>
          <p className="text-xs dark:text-untold-muted mt-1">Active runs</p>
        </div>
        <div className="ai-stat-card text-center">
          <p className="text-2xl font-bold text-untold-gold">{overview?.published_jobs ?? 0}</p>
          <p className="text-xs dark:text-untold-muted mt-1">Published</p>
        </div>
        <div className="ai-stat-card text-center">
          <p className="text-2xl font-bold text-untold-gold">{overview?.failed_jobs ?? 0}</p>
          <p className="text-xs dark:text-untold-muted mt-1">Failed</p>
        </div>
        <div className="ai-stat-card text-center">
          <p className="text-2xl font-bold text-untold-gold">{overview?.webhook_count ?? 0}</p>
          <p className="text-xs dark:text-untold-muted mt-1">Webhooks</p>
        </div>
        <div className="ai-stat-card text-center">
          <p className="text-2xl font-bold text-untold-gold">{overview?.total_runs ?? 0}</p>
          <p className="text-xs dark:text-untold-muted mt-1">Total runs</p>
        </div>
      </div>

      <div className="flex gap-1 border-b dark:border-white/10 pb-px flex-wrap">
        {PANELS.map((p) => (
          <button
            key={p}
            type="button"
            onClick={() => setPanel(p)}
            className={`px-3 py-2 text-xs font-medium border-b-2 -mb-px ${
              panel === p ? 'border-untold-gold text-untold-gold' : 'border-transparent dark:text-untold-muted'
            }`}
          >
            {PANEL_LABELS[p]}
          </button>
        ))}
      </div>

      <div className="rounded-xl border dark:border-white/10 p-5 dark:bg-untold-card/30 min-h-[420px]">
        {panel === 'dispatch' && (
          <DispatchPanel
            projects={projects}
            dispatching={mutations.dispatch.isPending}
            onDispatch={(d) => {
              mutations.dispatch.mutate(d);
              setPanel('queue');
            }}
          />
        )}
        {panel === 'queue' && <AgentQueuePanel queue={queue} mutations={mutations} />}
        {panel === 'history' && <AgentHistoryPanel history={history} mutations={mutations} />}
        {panel === 'analytics' && <AnalyticsPanel analytics={analytics} />}
        {panel === 'webhooks' && (
          <WebhooksPanel
            webhooks={webhooks}
            mutations={mutations}
            webhookEvents={overview?.webhook_events}
          />
        )}
      </div>
    </div>
  );
}
