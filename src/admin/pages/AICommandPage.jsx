import { Link } from 'react-router-dom';
import { AI_TEAM, PIPELINE_STEPS } from '../../data/studioData';
import { PRODUCTS, studioPath } from '../../config/ecosystem';
import StudioPageHeader from '../components/StudioPageHeader';
import PipelineBar from '../components/PipelineBar';
import StudioLiveBadge from '../components/StudioLiveBadge';
import StudioSectionLoader from '../components/StudioSectionLoader';
import { useStudioAgents } from '../hooks/useStudioData';

const STATUS_COLORS = {
  active: 'bg-emerald-500',
  idle: 'bg-amber-500',
  scheduled: 'bg-blue-500',
};

export default function AICommandPage() {
  const { data, loading, live } = useStudioAgents();
  const agents = data?.agents?.length ? data.agents : AI_TEAM.map((a) => ({
    id: a.id,
    role: a.role,
    description: a.description,
    status: a.status,
    tasks: a.tasks,
  }));

  const stats = data
    ? [
        { label: 'Agents Active', value: data.active_count },
        { label: 'Tasks in Queue', value: data.total_queued },
        { label: 'Completed Today', value: data.completed_today },
        { label: 'Avg. Pipeline Time', value: `${data.avg_pipeline_days}d` },
      ]
    : [
        { label: 'Agents Active', value: AI_TEAM.filter((a) => a.status === 'active').length },
        { label: 'Tasks in Queue', value: AI_TEAM.reduce((s, a) => s + a.tasks, 0) },
        { label: 'Completed Today', value: '—' },
        { label: 'Avg. Pipeline Time', value: '—' },
      ];

  return (
    <div className="space-y-8">
      <StudioPageHeader
        section="AI Agents"
        title="Agent Command Center"
        description="Research → Fact Check → Script → Storyboard → Voice → Editing → Thumbnail → SEO → Publishing → Analytics"
      >
        <StudioLiveBadge live={live} />
      </StudioPageHeader>
      <PipelineBar activeStep="storyboard" />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat) => (
          <div key={stat.label} className="ai-stat-card">
            <p className="text-2xl font-bold text-untold-gold">{stat.value}</p>
            <p className="text-xs dark:text-untold-muted light:text-gray-500 mt-1">{stat.label}</p>
          </div>
        ))}
      </div>

      {loading ? (
        <StudioSectionLoader rows={4} />
      ) : (
        <div className="grid sm:grid-cols-2 xl:grid-cols-3 gap-4">
          {agents.map((agent) => (
            <article key={agent.id} className="ai-agent-card">
              <div className="flex items-center justify-between mb-3 gap-2">
                <h2 className="font-semibold dark:text-white light:text-black text-sm">{agent.role}</h2>
                <span className={`w-2 h-2 rounded-full shrink-0 ${STATUS_COLORS[agent.status] || 'bg-gray-500'}`} />
              </div>
              <p className="text-sm dark:text-untold-muted light:text-gray-500 leading-relaxed">{agent.description}</p>
              <div className="mt-4 flex items-center justify-between text-xs">
                <span className="capitalize dark:text-untold-muted light:text-gray-400">{agent.status}</span>
                <span className="text-untold-gold font-semibold">{agent.tasks} queued</span>
              </div>
              <div className="mt-3 h-1.5 rounded-full dark:bg-white/10 light:bg-gray-200 overflow-hidden">
                <div
                  className="h-full bg-untold-gold rounded-full transition-all"
                  style={{ width: `${Math.min(100, agent.tasks * 7)}%` }}
                />
              </div>
            </article>
          ))}
        </div>
      )}

      <section className="ai-pipeline-panel">
        <h2 className="text-lg font-bold dark:text-white light:text-black mb-6">Content Pipeline</h2>
        <div className="flex flex-wrap gap-2">
          {PIPELINE_STEPS.map((step, i) => (
            <span key={step} className="ai-pipeline-chip">
              {i > 0 && <span className="text-untold-gold/50 mx-1">→</span>}
              {step}
            </span>
          ))}
        </div>
      </section>

      <p className="text-xs dark:text-untold-muted light:text-gray-400">
        View team roles in{' '}
        <Link to={studioPath('team')} className="text-untold-gold hover:underline">Human & AI Team</Link>
        , configure agents in{' '}
        <Link to={studioPath('ai-localization')} className="text-untold-gold hover:underline">AI Localization</Link>
        {' '}and publish to{' '}
        <Link to={studioPath('content')} className="text-untold-gold hover:underline">Content CMS</Link>
        {' '}→ {PRODUCTS.ORIGINALS.name}.
      </p>
    </div>
  );
}
