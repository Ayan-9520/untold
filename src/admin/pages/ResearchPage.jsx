import { Link } from 'react-router-dom';
import StudioPageHeader from '../components/StudioPageHeader';
import PipelineBar from '../components/PipelineBar';
import StudioLiveBadge from '../components/StudioLiveBadge';
import StudioSectionLoader from '../components/StudioSectionLoader';
import { PRODUCTS, studioPath } from '../../config/ecosystem';
import { useStudioProductions } from '../hooks/useStudioData';

const SOURCE_TYPES = [
  { icon: '📚', label: 'Books & archives' },
  { icon: '📰', label: 'Articles & press' },
  { icon: '🎤', label: 'Interviews' },
  { icon: '📹', label: 'Videos & footage' },
  { icon: '📊', label: 'Statistics & data' },
];

export default function ResearchPage() {
  const { items: inResearch, loading, live } = useStudioProductions('research');

  return (
    <div className="space-y-8">
      <StudioPageHeader
        section="Produce"
        title="Research"
        description={`Collect and verify sources before scripting. Feeds ${PRODUCTS.ORIGINALS.name} documentaries.`}
      >
        <StudioLiveBadge live={live} />
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
        <h2 className="text-sm font-semibold dark:text-white light:text-black mb-4">Active research</h2>
        {loading ? (
          <StudioSectionLoader rows={2} />
        ) : inResearch.length === 0 ? (
          <p className="text-sm dark:text-untold-muted light:text-gray-500">No productions in research stage.</p>
        ) : (
          <div className="space-y-2">
            {inResearch.map((p) => (
              <div key={p.id} className="studio-production-row">
                <div className="min-w-0 flex-1">
                  <p className="font-medium dark:text-white light:text-black text-sm truncate">{p.title}</p>
                  <p className="text-xs dark:text-untold-muted light:text-gray-500 mt-0.5">{p.assignee} · {p.sources} sources</p>
                </div>
                <Link to={studioPath('ai')} className="text-xs text-untold-gold hover:underline shrink-0">Open AI agents →</Link>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
