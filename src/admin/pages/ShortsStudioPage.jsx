import { useState } from 'react';
import StudioPageHeader from '../components/StudioPageHeader';
import StudioLiveBadge from '../components/StudioLiveBadge';
import { useShortsStudioOverview, useShortsQueue, useShortsHistory, useShortsStudioMutations } from '../features/shorts-studio/hooks/useShortsStudio';
import ShortsGeneratorPanel from '../features/shorts-studio/components/ShortsGeneratorPanel';
import { ShortsGallery, ShortsQueuePanel } from '../features/shorts-studio/components/ShortsGallery';
import { studioPlatform } from '../api/adminApi';

const PANELS = ['generate', 'history', 'queue'];
const PANEL_LABELS = { generate: 'Generate', history: 'History', queue: 'Queue' };

export default function ShortsStudioPage() {
  const [panel, setPanel] = useState('generate');
  const { data: overview, isError } = useShortsStudioOverview();
  const { data: queue } = useShortsQueue();
  const { data: history } = useShortsHistory();
  const mutations = useShortsStudioMutations();
  const counts = overview?.queue_counts || {};

  return (
    <div className="space-y-6">
      <StudioPageHeader section="AI Shorts Generator" title="Shorts Studio"
        description="Long video → highlights · Reels · Shorts · TikTok · 9:16 · Captions · Publish queue">
        <StudioLiveBadge live={!isError} />
      </StudioPageHeader>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {['Queued', 'Running', 'Completed', 'Failed'].map((label) => (
          <div key={label} className="ai-stat-card text-center">
            <p className="text-2xl font-bold text-untold-gold">{counts[label.toLowerCase()] ?? 0}</p>
            <p className="text-xs dark:text-untold-muted mt-1">{label}</p>
          </div>
        ))}
      </div>
      <div className="flex gap-1 border-b dark:border-white/10 pb-px">
        {PANELS.map((p) => (
          <button key={p} type="button" onClick={() => setPanel(p)}
            className={`px-3 py-2 text-xs font-medium border-b-2 -mb-px ${panel === p ? 'border-untold-gold text-untold-gold' : 'border-transparent dark:text-untold-muted'}`}>
            {PANEL_LABELS[p]}
          </button>
        ))}
      </div>
      <div className="rounded-xl border dark:border-white/10 p-5 dark:bg-untold-card/30 min-h-[420px]">
        {panel === 'generate' && (
          <ShortsGeneratorPanel overview={overview} generating={mutations.generate.isPending}
            onGenerate={(d) => { mutations.generate.mutate(d); setPanel('queue'); }} />
        )}
        {panel === 'history' && <ShortsGallery jobs={history?.items} mutations={mutations} getDownloadUrl={studioPlatform.getShortsDownloadUrl} />}
        {panel === 'queue' && <ShortsQueuePanel queue={queue} mutations={mutations} />}
      </div>
    </div>
  );
}
