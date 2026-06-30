import { Link } from 'react-router-dom';
import StudioPageHeader from '../components/StudioPageHeader';
import PipelineBar from '../components/PipelineBar';
import StudioLiveBadge from '../components/StudioLiveBadge';
import { PRODUCTS, studioPath } from '../../config/ecosystem';
import { useProjects } from '../features/projects/hooks/useProjects';
import { useScriptsSummary } from '../hooks/useStudioData';

const SCRIPT_FEATURES = [
  { icon: '✍️', label: 'Rich text editor' },
  { icon: '🤖', label: 'AI script writer' },
  { icon: '🎬', label: 'Broadcast styles' },
  { icon: '📝', label: 'Version history' },
  { icon: '💬', label: 'Comments' },
  { icon: '✅', label: 'Approval workflow' },
  { icon: '📤', label: 'Export MD/PDF/Word' },
];

export default function ScriptsPage() {
  const { data, isLoading, isError } = useProjects({ stage: 'script', limit: 50 });
  const { summary } = useScriptsSummary();
  const projects = data?.items || [];

  const draftCount = projects.filter((p) => p.status === 'draft').length;
  const reviewCount = projects.filter((p) => p.status === 'review').length;

  return (
    <div className="space-y-8">
      <StudioPageHeader
        section="Script Studio"
        title="Scripts"
        description="Write, collaborate, approve, and export documentary scripts before storyboard."
      >
        <StudioLiveBadge live={!isError} />
      </StudioPageHeader>
      <PipelineBar activeStep="script" />

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {[
          { label: 'Draft', count: draftCount },
          { label: 'In review', count: reviewCount },
          { label: 'Approved', count: summary.approved },
        ].map((s) => (
          <div key={s.label} className="ai-stat-card text-center">
            <p className="text-2xl font-bold text-untold-gold">{s.count}</p>
            <p className="text-xs dark:text-untold-muted light:text-gray-500 mt-1">{s.label}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        {SCRIPT_FEATURES.map((s) => (
          <div key={s.label} className="studio-module-card">
            <span className="text-2xl">{s.icon}</span>
            <p className="text-sm font-medium dark:text-white light:text-black mt-2">{s.label}</p>
          </div>
        ))}
      </div>

      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-semibold dark:text-white light:text-black">Script workspaces</h2>
          <Link to={studioPath('projects')} className="text-xs text-untold-gold hover:underline">All projects →</Link>
        </div>
        {isLoading ? (
          <div className="h-32 skeleton rounded-xl" />
        ) : projects.length === 0 ? (
          <div className="rounded-xl border dark:border-white/10 p-8 text-center">
            <p className="text-sm dark:text-untold-muted">No projects in script stage.</p>
            <Link to={studioPath('projects')} className="text-sm text-untold-gold mt-2 inline-block">Create a project →</Link>
          </div>
        ) : (
          <div className="grid gap-3 sm:grid-cols-2">
            {projects.map((p) => (
              <Link
                key={p.id}
                to={studioPath(`scripts/${p.id}`)}
                className="studio-production-row hover:border-untold-gold/30 transition-colors"
              >
                <div className="min-w-0 flex-1">
                  <p className="font-medium dark:text-white light:text-black text-sm truncate">{p.title}</p>
                  <p className="text-xs dark:text-untold-muted light:text-gray-500 mt-0.5 capitalize">
                    {p.status} · v{p.version} · {p.assignee}
                  </p>
                </div>
                <span className="text-xs text-untold-gold shrink-0">Open editor →</span>
              </Link>
            ))}
          </div>
        )}
      </section>

      <p className="text-xs dark:text-untold-muted light:text-gray-400">
        Approved scripts publish to <Link to={studioPath('content')} className="text-untold-gold hover:underline">Publishing CMS</Link> → {PRODUCTS.ORIGINALS.name}.
      </p>
    </div>
  );
}
