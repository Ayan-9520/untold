import { Link } from 'react-router-dom';
import StudioPageHeader from '../components/StudioPageHeader';
import PipelineBar from '../components/PipelineBar';
import StudioLiveBadge from '../components/StudioLiveBadge';
import StudioSectionLoader from '../components/StudioSectionLoader';
import { PRODUCTS, studioPath } from '../../config/ecosystem';
import { useStudioProductions, useScriptsSummary } from '../hooks/useStudioData';

export default function ScriptsPage() {
  const { items: inScript, loading, live } = useStudioProductions('script');
  const { summary } = useScriptsSummary();

  const draftCount = inScript.filter((p) => p.status === 'draft').length;
  const reviewCount = inScript.filter((p) => p.status === 'review').length;

  return (
    <div className="space-y-8">
      <StudioPageHeader
        section="Produce"
        title="Scripts"
        description="Generate, edit, approve, and version documentary scripts before storyboard and edit."
      >
        <StudioLiveBadge live={live} />
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

      <section>
        <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
          <h2 className="text-sm font-semibold dark:text-white light:text-black">Script queue</h2>
          <Link to={studioPath('content')} className="text-xs text-untold-gold hover:underline">Full CMS →</Link>
        </div>
        {loading ? (
          <StudioSectionLoader rows={3} />
        ) : (
          <div className="space-y-2">
            {inScript.map((p) => (
              <div key={p.id} className="studio-production-row">
                <div className="min-w-0 flex-1">
                  <p className="font-medium dark:text-white light:text-black text-sm truncate">{p.title}</p>
                  <p className="text-xs dark:text-untold-muted light:text-gray-500 mt-0.5 capitalize">{p.status} · v{p.version}</p>
                </div>
                <span className="text-xs px-2 py-0.5 rounded-full bg-untold-gold/15 text-untold-gold shrink-0">{p.assignee}</span>
              </div>
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
