import { Link } from 'react-router-dom';
import StudioPageHeader from '../components/StudioPageHeader';
import PipelineBar from '../components/PipelineBar';
import StudioLiveBadge from '../components/StudioLiveBadge';
import { PRODUCTS, studioPath } from '../../config/ecosystem';
import { useProjects } from '../features/projects/hooks/useProjects';

const SOURCE_TYPES = [
  { icon: '📚', label: 'Books & archives' },
  { icon: '📰', label: 'Articles & press' },
  { icon: '🎤', label: 'Interviews' },
  { icon: '📹', label: 'Videos & footage' },
  { icon: '📊', label: 'Statistics & data' },
];

export default function ResearchPage() {
  const { data, isLoading, isError } = useProjects({ stage: 'research', limit: 50 });
  const projects = data?.items || [];

  return (
    <div className="space-y-8">
      <StudioPageHeader
        section="Research Studio"
        title="Research"
        description={`Collect, verify, and export sources before scripting. Feeds ${PRODUCTS.ORIGINALS.name} documentaries.`}
      >
        <StudioLiveBadge live={!isError} />
      </StudioPageHeader>
      <PipelineBar activeStep="research" />

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
        {SOURCE_TYPES.map((s) => (
          <div key={s.label} className="studio-module-card">
            <span className="text-2xl">{s.icon}</span>
            <p className="text-sm font-medium dark:text-white light:text-black mt-2">{s.label}</p>
          </div>
        ))}
      </div>

      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-semibold dark:text-white light:text-black">Research workspaces</h2>
          <Link to={studioPath('projects')} className="text-xs text-untold-gold hover:underline">All projects →</Link>
        </div>
        {isLoading ? (
          <div className="h-32 skeleton rounded-xl" />
        ) : projects.length === 0 ? (
          <div className="rounded-xl border dark:border-white/10 p-8 text-center">
            <p className="text-sm dark:text-untold-muted">No projects in research stage.</p>
            <Link to={studioPath('projects')} className="text-sm text-untold-gold mt-2 inline-block">Create a project →</Link>
          </div>
        ) : (
          <div className="grid gap-3 sm:grid-cols-2">
            {projects.map((p) => (
              <Link
                key={p.id}
                to={studioPath(`research/${p.id}`)}
                className="studio-production-row hover:border-untold-gold/30 transition-colors"
              >
                <div className="min-w-0 flex-1">
                  <p className="font-medium dark:text-white light:text-black text-sm truncate">{p.title}</p>
                  <p className="text-xs dark:text-untold-muted light:text-gray-500 mt-0.5">
                    {p.assignee} · {p.sources_count} sources
                  </p>
                </div>
                <span className="text-xs text-untold-gold shrink-0">Open workspace →</span>
              </Link>
            ))}
          </div>
        )}
      </section>

      <section className="rounded-xl border dark:border-white/10 p-5 dark:bg-untold-card/20">
        <h3 className="text-sm font-semibold dark:text-white mb-2">Research Studio includes</h3>
        <p className="text-xs dark:text-untold-muted leading-relaxed">
          Conversation · research workspace · references · prompt history · previous outputs · user preferences ·
          project switcher · AI agent · fact-check · version history · export to Markdown, PDF & Word.
        </p>
      </section>
    </div>
  );
}
