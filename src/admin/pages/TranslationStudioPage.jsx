import { useState } from 'react';
import StudioPageHeader from '../components/StudioPageHeader';
import PipelineBar from '../components/PipelineBar';
import StudioLiveBadge from '../components/StudioLiveBadge';
import {
  useTranslationStudioOverview,
  useTranslationQueue,
  useTranslationHistory,
  useTranslationMemory,
  useTranslationStudioMutations,
} from '../features/translation-studio/hooks/useTranslationStudio';
import TranslationGeneratorPanel from '../features/translation-studio/components/TranslationGeneratorPanel';
import {
  TranslationHistoryPanel,
  TranslationQueuePanel,
  TranslationMemoryPanel,
} from '../features/translation-studio/components/TranslationPanels';

const PANELS = ['generate', 'history', 'queue', 'memory'];
const PANEL_LABELS = {
  generate: 'Translate',
  history: 'History',
  queue: 'Queue',
  memory: 'Translation Memory',
};

export default function TranslationStudioPage() {
  const [panel, setPanel] = useState('generate');
  const { data: overview, isError } = useTranslationStudioOverview();
  const { data: queue } = useTranslationQueue();
  const { data: history } = useTranslationHistory();
  const { data: memory } = useTranslationMemory();
  const mutations = useTranslationStudioMutations();
  const counts = overview?.queue_counts || {};

  return (
    <div className="studio-page space-y-6">
      <StudioPageHeader
        section="AI Translation Studio"
        title="Translation Studio"
        description="Scripts · Voice · Subtitles · Metadata · SRT/VTT · Auto-sync · TM · Approval"
      >
        <StudioLiveBadge live={!isError} />
      </StudioPageHeader>

      <PipelineBar activeStep="translation" />

      <div className="grid grid-cols-2 lg:grid-cols-5 gap-3">
        {['Queued', 'Running', 'Completed', 'Failed'].map((label) => (
          <div key={label} className="ai-stat-card text-center">
            <p className="text-2xl font-bold text-untold-gold">{counts[label.toLowerCase()] ?? 0}</p>
            <p className="text-xs studio-muted mt-1">{label}</p>
          </div>
        ))}
        <div className="ai-stat-card text-center">
          <p className="text-2xl font-bold text-untold-gold">{overview?.translation_memory_count ?? 0}</p>
          <p className="text-xs studio-muted mt-1">TM entries</p>
        </div>
      </div>

      <div className="studio-tab-bar flex-wrap">
        {PANELS.map((p) => (
          <button
            key={p}
            type="button"
            onClick={() => setPanel(p)}
            className={`studio-tab ${panel === p ? 'studio-tab--active' : ''}`}
          >
            {PANEL_LABELS[p]}
          </button>
        ))}
      </div>

      <div className="studio-card p-5 min-h-[420px]">
        {panel === 'generate' && (
          <TranslationGeneratorPanel
            overview={overview}
            translating={mutations.translate.isPending}
            onTranslate={(d) => {
              mutations.translate.mutate(d);
              setPanel('queue');
            }}
          />
        )}
        {panel === 'history' && (
          <TranslationHistoryPanel
            jobs={history?.items}
            mutations={mutations}
            languages={overview?.languages}
          />
        )}
        {panel === 'queue' && <TranslationQueuePanel queue={queue} mutations={mutations} />}
        {panel === 'memory' && (
          <TranslationMemoryPanel
            memory={memory}
            mutations={mutations}
            languages={overview?.languages}
          />
        )}
      </div>
    </div>
  );
}
