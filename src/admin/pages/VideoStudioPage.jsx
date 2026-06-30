import { useState } from 'react';
import StudioPageHeader from '../components/StudioPageHeader';
import PipelineBar from '../components/PipelineBar';
import StudioLiveBadge from '../components/StudioLiveBadge';
import {
  useVideoStudioOverview,
  useVideoQueue,
  useVideoHistory,
  useVideoPrompts,
  useVideoStudioMutations,
} from '../features/video-studio/hooks/useVideoStudio';
import VideoGeneratorPanel from '../features/video-studio/components/VideoGeneratorPanel';
import { VideoGallery, VideoQueuePanel } from '../features/video-studio/components/VideoGallery';
import VideoPromptLibrary from '../features/video-studio/components/VideoPromptLibrary';
import { studioPlatform } from '../api/adminApi';

const PANELS = ['generate', 'history', 'queue', 'prompts'];
const PANEL_LABELS = {
  generate: 'Generate',
  history: 'History',
  queue: 'Queue',
  prompts: 'Prompt Library',
};

export default function VideoStudioPage() {
  const [panel, setPanel] = useState('generate');
  const [videoType, setVideoType] = useState('b_roll');
  const [promptPrefill, setPromptPrefill] = useState('');

  const { data: overview, isError } = useVideoStudioOverview();
  const { data: queue } = useVideoQueue();
  const { data: history } = useVideoHistory(videoType);
  const { data: prompts } = useVideoPrompts(videoType);
  const mutations = useVideoStudioMutations();

  const counts = overview?.queue_counts || {};

  return (
    <div className="space-y-6">
      <StudioPageHeader
        section="AI Video Studio"
        title="Video Studio"
        description="B-roll · Drone · Animation · Sports Intro · Motion Graphics · Queue · Storage"
      >
        <StudioLiveBadge live={!isError} />
      </StudioPageHeader>

      <PipelineBar activeStep="video" />

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
          <VideoGeneratorPanel
            key={`${videoType}-${promptPrefill}`}
            providers={overview?.providers}
            videoType={videoType}
            onTypeChange={setVideoType}
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
          <VideoGallery
            jobs={history?.items}
            mutations={mutations}
            getDownloadUrl={studioPlatform.getVideoDownloadUrl}
          />
        )}
        {panel === 'queue' && <VideoQueuePanel queue={queue} mutations={mutations} />}
        {panel === 'prompts' && (
          <VideoPromptLibrary
            prompts={prompts}
            videoType={videoType}
            onUse={(p) => {
              if (p.parameters?.video_type) setVideoType(p.parameters.video_type);
              setPromptPrefill(p.prompt_template);
              setPanel('generate');
            }}
          />
        )}
      </div>
    </div>
  );
}
