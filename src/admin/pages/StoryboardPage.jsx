import { Link } from 'react-router-dom';
import StudioPageHeader from '../components/StudioPageHeader';
import PipelineBar from '../components/PipelineBar';
import StudioLiveBadge from '../components/StudioLiveBadge';
import { studioPath } from '../../config/ecosystem';
import { useProjects } from '../features/projects/hooks/useProjects';

const FEATURES = [
  { icon: '🤖', label: 'AI generator' },
  { icon: '🎬', label: 'Script → scenes' },
  { icon: '↕️', label: 'Drag & reorder' },
  { icon: '🎭', label: 'Mood & transitions' },
  { icon: '📷', label: 'Camera & lighting' },
  { icon: '✅', label: 'Approval workflow' },
];

export default function StoryboardPage() {
  const { data, isLoading, isError } = useProjects({ stage: 'storyboard', limit: 50 });
  const projects = data?.items || [];

  return (
    <div className="space-y-8">
      <StudioPageHeader
        section="Storyboard Studio"
        title="Storyboard"
        description="Convert approved scripts into visual scene plans with narration, camera, and references."
      >
        <StudioLiveBadge live={!isError} />
      </StudioPageHeader>
      <PipelineBar activeStep="storyboard" />

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        {FEATURES.map((f) => (
          <div key={f.label} className="studio-module-card">
            <span className="text-2xl">{f.icon}</span>
            <p className="text-sm font-medium dark:text-white light:text-black mt-2">{f.label}</p>
          </div>
        ))}
      </div>

      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-semibold dark:text-white light:text-black">Storyboard workspaces</h2>
          <Link to={studioPath('projects')} className="text-xs text-untold-gold hover:underline">All projects →</Link>
        </div>
        {isLoading ? (
          <div className="h-32 skeleton rounded-xl" />
        ) : projects.length === 0 ? (
          <div className="rounded-xl border dark:border-white/10 p-8 text-center">
            <p className="text-sm dark:text-untold-muted">No projects in storyboard stage.</p>
            <Link to={studioPath('projects')} className="text-sm text-untold-gold mt-2 inline-block">Move a project to storyboard →</Link>
          </div>
        ) : (
          <div className="grid gap-3 sm:grid-cols-2">
            {projects.map((p) => (
              <Link
                key={p.id}
                to={studioPath(`storyboard/${p.id}`)}
                className="studio-production-row hover:border-untold-gold/30 transition-colors"
              >
                <div className="min-w-0 flex-1">
                  <p className="font-medium dark:text-white light:text-black text-sm truncate">{p.title}</p>
                  <p className="text-xs dark:text-untold-muted light:text-gray-500 mt-0.5 capitalize">
                    {p.status} · v{p.version} · {p.assignee}
                  </p>
                </div>
                <span className="text-xs text-untold-gold shrink-0">Open storyboard →</span>
              </Link>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
