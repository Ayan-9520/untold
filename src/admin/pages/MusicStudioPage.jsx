import { useState } from 'react';
import StudioPageHeader from '../components/StudioPageHeader';
import PipelineBar from '../components/PipelineBar';
import StudioLiveBadge from '../components/StudioLiveBadge';
import {
  useMusicStudioOverview,
  useMusicQueue,
  useMusicHistory,
  useMusicFavorites,
  useMusicPrompts,
  useMusicStudioMutations,
} from '../features/music-studio/hooks/useMusicStudio';
import MusicGeneratorPanel from '../features/music-studio/components/MusicGeneratorPanel';
import { MusicGallery, MusicQueuePanel } from '../features/music-studio/components/MusicGallery';
import MusicPromptLibrary from '../features/music-studio/components/MusicPromptLibrary';
import { studioPlatform } from '../api/adminApi';

const PANELS = ['generate', 'history', 'favorites', 'queue', 'prompts'];
const PANEL_LABELS = {
  generate: 'Generate',
  history: 'History',
  favorites: 'Favorites',
  queue: 'Queue',
  prompts: 'Brief Library',
};

export default function MusicStudioPage() {
  const [panel, setPanel] = useState('generate');
  const [category, setCategory] = useState('documentary');
  const [promptPrefill, setPromptPrefill] = useState('');

  const { data: overview, isError } = useMusicStudioOverview();
  const { data: queue } = useMusicQueue();
  const { data: history } = useMusicHistory(category);
  const { data: favorites } = useMusicFavorites();
  const { data: prompts } = useMusicPrompts(category);
  const mutations = useMusicStudioMutations();

  const counts = overview?.queue_counts || {};

  return (
    <div className="space-y-6">
      <StudioPageHeader
        section="AI Music Studio"
        title="Music Studio"
        description="Background music · 7 categories · Duration · Loop · Fade · Favorites · Cloud storage"
      >
        <StudioLiveBadge live={!isError} />
      </StudioPageHeader>

      <PipelineBar activeStep="music" />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {[
          { label: 'Queued', value: counts.queued ?? 0 },
          { label: 'Running', value: counts.running ?? 0 },
          { label: 'Completed', value: counts.completed ?? 0 },
          { label: 'Failed', value: counts.failed ?? 0 },
        ].map((s) => (
          <div key={s.label} className="ai-stat-card text-center">
            <p className="text-2xl font-bold text-untold-gold">{s.value}</p>
            <p className="text-xs dark:text-untold-muted mt-1">{s.label}</p>
          </div>
        ))}
      </div>

      <div className="flex gap-1 overflow-x-auto border-b dark:border-white/10 pb-px">
        {PANELS.map((p) => (
          <button
            key={p}
            type="button"
            onClick={() => setPanel(p)}
            className={`px-3 py-2 text-xs font-medium whitespace-nowrap border-b-2 -mb-px transition-colors ${
              panel === p ? 'border-untold-gold text-untold-gold' : 'border-transparent dark:text-untold-muted'
            }`}
          >
            {PANEL_LABELS[p]}
          </button>
        ))}
      </div>

      <div className="rounded-xl border dark:border-white/10 p-5 dark:bg-untold-card/30 min-h-[420px]">
        {panel === 'generate' && (
          <MusicGeneratorPanel
            key={`${category}-${promptPrefill}`}
            providers={overview?.providers}
            category={category}
            onCategoryChange={setCategory}
            initialPrompt={promptPrefill}
            generating={mutations.generate.isPending}
            previewing={mutations.preview.isPending}
            onPreview={(data) => mutations.preview.mutateAsync(data)}
            onGenerate={(data) => {
              mutations.generate.mutate(data);
              setPromptPrefill('');
              setPanel('queue');
            }}
          />
        )}
        {panel === 'history' && (
          <MusicGallery
            jobs={history?.items}
            mutations={mutations}
            getDownloadUrl={studioPlatform.getMusicDownloadUrl}
          />
        )}
        {panel === 'favorites' && (
          <MusicGallery
            jobs={favorites}
            mutations={mutations}
            getDownloadUrl={studioPlatform.getMusicDownloadUrl}
          />
        )}
        {panel === 'queue' && <MusicQueuePanel queue={queue} mutations={mutations} />}
        {panel === 'prompts' && (
          <MusicPromptLibrary
            prompts={prompts}
            category={category}
            onUse={(p) => {
              if (p.parameters?.category) setCategory(p.parameters.category);
              setPromptPrefill(p.prompt_template);
              setPanel('generate');
            }}
          />
        )}
      </div>
    </div>
  );
}
