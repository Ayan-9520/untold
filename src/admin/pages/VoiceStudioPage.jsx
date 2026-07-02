import { useState } from 'react';
import StudioPageHeader from '../components/StudioPageHeader';
import PipelineBar from '../components/PipelineBar';
import StudioLiveBadge from '../components/StudioLiveBadge';
import {
  useVoiceStudioOverview,
  useVoiceQueue,
  useVoiceHistory,
  useVoicePrompts,
  useVoiceStudioMutations,
} from '../features/voice-studio/hooks/useVoiceStudio';
import VoiceGeneratorPanel from '../features/voice-studio/components/VoiceGeneratorPanel';
import { VoiceGallery, VoiceQueuePanel } from '../features/voice-studio/components/VoiceGallery';
import VoicePromptLibrary from '../features/voice-studio/components/VoicePromptLibrary';
import { studioPlatform } from '../api/adminApi';

const PANELS = ['generate', 'history', 'queue', 'prompts'];
const PANEL_LABELS = {
  generate: 'Generate',
  history: 'History',
  queue: 'Queue',
  prompts: 'Script Library',
};

export default function VoiceStudioPage() {
  const [panel, setPanel] = useState('generate');
  const [language, setLanguage] = useState('en');
  const [textPrefill, setTextPrefill] = useState('');

  const { data: overview, isError } = useVoiceStudioOverview();
  const { data: queue } = useVoiceQueue();
  const { data: history } = useVoiceHistory(language);
  const { data: prompts } = useVoicePrompts(language);
  const mutations = useVoiceStudioMutations();

  const counts = overview?.queue_counts || {};

  return (
    <div className="studio-page space-y-6">
      <StudioPageHeader
        section="AI Voice Studio"
        title="Voice Studio"
        description="Narration · 6 languages · Emotion · Pitch · Speed · Subtitles · Translation"
      >
        <StudioLiveBadge live={!isError} />
      </StudioPageHeader>

      <PipelineBar activeStep="voice" />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {[
          { label: 'Queued', value: counts.queued ?? 0 },
          { label: 'Running', value: counts.running ?? 0 },
          { label: 'Completed', value: counts.completed ?? 0 },
          { label: 'Failed', value: counts.failed ?? 0 },
        ].map((s) => (
          <div key={s.label} className="ai-stat-card text-center">
            <p className="text-2xl font-bold text-untold-gold">{s.value}</p>
            <p className="text-xs studio-muted mt-1">{s.label}</p>
          </div>
        ))}
      </div>

      <div className="studio-tab-bar">
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
          <VoiceGeneratorPanel
            key={`${language}-${textPrefill}`}
            overview={overview}
            language={language}
            onLanguageChange={setLanguage}
            initialText={textPrefill}
            generating={mutations.generate.isPending}
            previewing={mutations.preview.isPending}
            translating={mutations.translate.isPending}
            onPreview={(data) => mutations.preview.mutateAsync(data)}
            onTranslate={(data) => mutations.translate.mutateAsync(data)}
            onGenerate={(data) => {
              mutations.generate.mutate(data);
              setTextPrefill('');
              setPanel('queue');
            }}
          />
        )}
        {panel === 'history' && (
          <VoiceGallery
            jobs={history?.items}
            mutations={mutations}
            getDownloadUrl={studioPlatform.getVoiceDownloadUrl}
            getSubtitlesUrl={studioPlatform.getVoiceSubtitlesUrl}
          />
        )}
        {panel === 'queue' && <VoiceQueuePanel queue={queue} mutations={mutations} />}
        {panel === 'prompts' && (
          <VoicePromptLibrary
            prompts={prompts}
            language={language}
            onUse={(p) => {
              if (p.parameters?.language) setLanguage(p.parameters.language);
              setTextPrefill(p.prompt_template);
              setPanel('generate');
            }}
          />
        )}
      </div>
    </div>
  );
}
