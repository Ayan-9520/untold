import { Link } from 'react-router-dom';
import StudioPageHeader from '../components/StudioPageHeader';
import PipelineBar from '../components/PipelineBar';
import StudioLiveBadge from '../components/StudioLiveBadge';
import { studioPath } from '../../config/ecosystem';
import { useProjects } from '../features/projects/hooks/useProjects';

const FEATURES = [
  { icon: '🎬', label: 'Video tracks' },
  { icon: '🎵', label: 'Audio + waveform' },
  { icon: '🖼️', label: 'Image overlays' },
  { icon: '✏️', label: 'Text layers' },
  { icon: '✨', label: 'Transitions' },
  { icon: '💬', label: 'Captions' },
  { icon: '✂', label: 'Trim · Split · Merge' },
  { icon: '↶', label: 'Undo / Redo' },
  { icon: '📤', label: 'Export queue' },
  { icon: '⌨️', label: 'Keyboard shortcuts' },
  { icon: '💾', label: 'Autosave' },
];

export default function TimelinePage() {
  const { data, isLoading, isError } = useProjects({ stage: 'editing', limit: 50 });
  const projects = data?.items || [];

  return (
    <div className="space-y-8">
      <StudioPageHeader
        section="Timeline Editor"
        title="Timeline Editor"
        description="Non-linear editor with modular engine — video, audio, images, text, transitions & captions."
      >
        <StudioLiveBadge live={!isError} />
      </StudioPageHeader>
      <PipelineBar activeStep="timeline" />

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
          <h2 className="text-sm font-semibold dark:text-white light:text-black">Editing workspaces</h2>
          <Link to={studioPath('projects')} className="text-xs text-untold-gold hover:underline">All projects →</Link>
        </div>
        {isLoading ? (
          <div className="h-32 skeleton rounded-xl" />
        ) : projects.length === 0 ? (
          <div className="rounded-xl border dark:border-white/10 p-8 text-center">
            <p className="text-sm dark:text-untold-muted">No projects in editing stage.</p>
            <Link to={studioPath('projects')} className="text-sm text-untold-gold mt-2 inline-block">Move a project to editing →</Link>
          </div>
        ) : (
          <div className="grid gap-3 sm:grid-cols-2">
            {projects.map((p) => (
              <Link
                key={p.id}
                to={studioPath(`timeline/${p.id}`)}
                className="studio-production-row hover:border-untold-gold/30 transition-colors"
              >
                <div className="min-w-0 flex-1">
                  <p className="font-medium dark:text-white light:text-black text-sm truncate">{p.title}</p>
                  <p className="text-xs dark:text-untold-muted light:text-gray-500 mt-0.5 capitalize">
                    {p.status} · v{p.version} · {p.assignee}
                  </p>
                </div>
                <span className="text-xs text-untold-gold shrink-0">Open timeline →</span>
              </Link>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
