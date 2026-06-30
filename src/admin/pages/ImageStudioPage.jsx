import { useState } from 'react';
import StudioPageHeader from '../components/StudioPageHeader';
import PipelineBar from '../components/PipelineBar';
import StudioLiveBadge from '../components/StudioLiveBadge';
import {
  useImageStudioOverview,
  useImageQueue,
  useImageHistory,
  useImageFavorites,
  useImageCollections,
  useImagePrompts,
  useImageStudioMutations,
} from '../features/image-studio/hooks/useImageStudio';
import ImageGeneratorPanel from '../features/image-studio/components/ImageGeneratorPanel';
import { ImageGallery, ImageQueuePanel } from '../features/image-studio/components/ImageGallery';
import ImagePromptLibrary, { CollectionsPanel } from '../features/image-studio/components/ImagePromptLibrary';
import { studioPlatform } from '../api/adminApi';

const PANELS = ['generate', 'history', 'favorites', 'queue', 'prompts', 'collections'];
const PANEL_LABELS = {
  generate: 'Generate',
  history: 'History',
  favorites: 'Favorites',
  queue: 'Queue',
  prompts: 'Prompt Library',
  collections: 'Collections',
};

export default function ImageStudioPage() {
  const [panel, setPanel] = useState('generate');
  const [imageType, setImageType] = useState('poster');
  const [promptPrefill, setPromptPrefill] = useState('');

  const { data: overview, isError } = useImageStudioOverview();
  const { data: queue } = useImageQueue();
  const { data: history } = useImageHistory(imageType);
  const { data: favorites } = useImageFavorites();
  const { data: collections } = useImageCollections();
  const { data: prompts } = useImagePrompts(imageType);
  const mutations = useImageStudioMutations();

  const counts = overview?.queue_counts || {};

  return (
    <div className="space-y-6">
      <StudioPageHeader
        section="AI Image Studio"
        title="Image Studio"
        description="Poster · Thumbnail · Concept art · Sports · Upscale · Variations · Cloud storage"
      >
        <StudioLiveBadge live={!isError} />
      </StudioPageHeader>

      <PipelineBar activeStep="image" />

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
          <ImageGeneratorPanel
            key={`${imageType}-${promptPrefill}`}
            providers={overview?.providers}
            imageType={imageType}
            onTypeChange={setImageType}
            initialPrompt={promptPrefill}
            generating={mutations.generate.isPending}
            onGenerate={(data) => {
              mutations.generate.mutate(data);
              setPromptPrefill('');
              setPanel('queue');
            }}
          />
        )}
        {panel === 'history' && (
          <ImageGallery
            jobs={history?.items}
            collections={collections}
            mutations={mutations}
            getDownloadUrl={studioPlatform.getImageDownloadUrl}
          />
        )}
        {panel === 'favorites' && (
          <ImageGallery
            jobs={favorites}
            collections={collections}
            mutations={mutations}
            getDownloadUrl={studioPlatform.getImageDownloadUrl}
          />
        )}
        {panel === 'queue' && <ImageQueuePanel queue={queue} mutations={mutations} />}
        {panel === 'prompts' && (
          <ImagePromptLibrary
            prompts={prompts}
            imageType={imageType}
            onUse={(p) => {
              if (p.parameters?.image_type) setImageType(p.parameters.image_type);
              setPromptPrefill(p.prompt_template);
              setPanel('generate');
            }}
          />
        )}
        {panel === 'collections' && (
          <CollectionsPanel
            collections={collections}
            creating={mutations.createCollection.isPending}
            onCreate={(data) => mutations.createCollection.mutate(data)}
          />
        )}
      </div>
    </div>
  );
}
