import { useState } from 'react';
import StudioPageHeader from '../components/StudioPageHeader';
import StudioLiveBadge from '../components/StudioLiveBadge';
import { AI_MODULES } from '../features/ai-studio/constants';
import {
  useAIStudioOverview,
  useAIQueue,
  useAIHistory,
  useAITelemetry,
  useAIPrompts,
  useAIStudioMutations,
} from '../features/ai-studio/hooks/useAIStudio';
import ModulePanel from '../features/ai-studio/components/ModulePanel';
import PromptLibraryPanel from '../features/ai-studio/components/PromptLibraryPanel';
import GenerationQueue, { GenerationHistory } from '../features/ai-studio/components/GenerationJobs';
import AITelemetryTable from '../features/ai-studio/components/AITelemetryTable';

const SIDEBAR_SECTIONS = ['modules', 'prompts', 'queue', 'history', 'telemetry'];

const SECTION_LABELS = {
  modules: 'Generate',
  prompts: 'Prompt Library',
  queue: 'Queue',
  history: 'History',
  telemetry: 'Telemetry',
};

export default function AICommandPage() {
  const [activeModule, setActiveModule] = useState('research');
  const [sidebar, setSidebar] = useState('modules');
  const [promptPrefill, setPromptPrefill] = useState('');

  const { data: overview, isError } = useAIStudioOverview();
  const { data: queue } = useAIQueue();
  const { data: history } = useAIHistory(activeModule);
  const { data: telemetry, isLoading: telemetryLoading } = useAITelemetry(activeModule);
  const { data: prompts } = useAIPrompts(null);
  const mutations = useAIStudioMutations();

  const modules = (overview?.modules || []).map((m) => {
    const local = AI_MODULES.find((x) => x.id === m.id);
    return { ...m, icon: local?.icon || '✨' };
  });
  const current = modules.find((m) => m.id === activeModule) || {
    id: activeModule,
    label: activeModule,
    description: '',
    icon: '✨',
  };

  const counts = overview?.queue_counts || {};
  const stats = [
    { label: 'Queued', value: counts.queued ?? 0 },
    { label: 'Running', value: counts.running ?? 0 },
    { label: 'Completed', value: counts.completed ?? 0 },
    { label: 'Failed', value: counts.failed ?? 0 },
  ];

  return (
    <div className="space-y-6">
      <StudioPageHeader
        section="AI Studio"
        title="AI Studio"
        description="Research · Script · Image · Video · Voice · Music · Thumbnail · SEO · Translation — provider-agnostic generation"
      >
        <StudioLiveBadge live={!isError} />
      </StudioPageHeader>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {stats.map((s) => (
          <div key={s.label} className="ai-stat-card text-center">
            <p className="text-2xl font-bold text-untold-gold">{s.value}</p>
            <p className="text-xs dark:text-untold-muted mt-1">{s.label}</p>
          </div>
        ))}
      </div>

      <div className="grid lg:grid-cols-[200px_1fr_320px] gap-6">
        <nav className="space-y-1">
          <p className="text-[10px] uppercase tracking-wider dark:text-untold-muted mb-2 px-2">Modules</p>
          {modules.map((m) => (
            <button
              key={m.id}
              type="button"
              onClick={() => { setActiveModule(m.id); setSidebar('modules'); }}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors ${
                activeModule === m.id && sidebar === 'modules'
                  ? 'bg-untold-gold/15 text-untold-gold'
                  : 'dark:text-untold-muted hover:bg-white/5'
              }`}
            >
              <span className="mr-2">{m.icon}</span>
              {m.label}
            </button>
          ))}
          <p className="text-[10px] uppercase tracking-wider dark:text-untold-muted mt-4 mb-2 px-2">Studio</p>
          {SIDEBAR_SECTIONS.slice(1).map((s) => (
            <button
              key={s}
              type="button"
              onClick={() => setSidebar(s)}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm capitalize transition-colors ${
                sidebar === s ? 'bg-untold-gold/15 text-untold-gold' : 'dark:text-untold-muted hover:bg-white/5'
              }`}
            >
              {SECTION_LABELS[s]}
            </button>
          ))}
        </nav>

        <div className="rounded-xl border dark:border-white/10 p-5 dark:bg-untold-card/30 min-h-[420px]">
          {sidebar === 'modules' && (
            <ModulePanel
              key={`${activeModule}-${promptPrefill}`}
              module={current}
              providers={overview?.providers || []}
              generating={mutations.generate.isPending}
              initialPrompt={promptPrefill}
              onGenerate={(data) => {
                mutations.generate.mutate(data);
                setPromptPrefill('');
              }}
            />
          )}
          {sidebar === 'prompts' && (
            <PromptLibraryPanel
              prompts={prompts || []}
              activeModule={activeModule}
              creating={mutations.createPrompt.isPending}
              onCreate={(data) => mutations.createPrompt.mutate(data)}
              onUse={(p) => {
                setActiveModule(p.module);
                setPromptPrefill(p.prompt_template);
                setSidebar('modules');
              }}
            />
          )}
          {sidebar === 'queue' && (
            <GenerationQueue
              queue={queue}
              onRetry={(id) => mutations.retryJob.mutate(id)}
              onCancel={(id) => mutations.cancelJob.mutate(id)}
            />
          )}
          {sidebar === 'history' && (
            <GenerationHistory
              history={history}
              onRetry={(id) => mutations.retryJob.mutate(id)}
              onCancel={(id) => mutations.cancelJob.mutate(id)}
            />
          )}
          {sidebar === 'telemetry' && (
            <AITelemetryTable data={telemetry} loading={telemetryLoading} />
          )}
        </div>

        <aside className="space-y-4">
          <div className="rounded-xl border dark:border-white/10 p-4">
            <p className="text-xs font-semibold dark:text-white mb-2">Providers</p>
            <ul className="space-y-2">
              {(overview?.providers || []).map((p) => (
                <li key={p.id} className="flex items-center justify-between text-xs">
                  <span className="dark:text-untold-muted">{p.label}</span>
                  <span className={p.available ? 'text-emerald-400' : 'text-gray-500'}>
                    {p.available ? 'ready' : 'off'}
                  </span>
                </li>
              ))}
            </ul>
            <p className="text-[10px] dark:text-untold-muted mt-3 leading-relaxed">
              Providers are pluggable via registry. Set AI_DEFAULT_PROVIDER and AI_ENABLED_PROVIDERS in env.
            </p>
          </div>
          <div className="rounded-xl border dark:border-white/10 p-4">
            <p className="text-xs font-semibold dark:text-white mb-2">Live queue</p>
            <GenerationQueue
              queue={queue}
              onRetry={(id) => mutations.retryJob.mutate(id)}
              onCancel={(id) => mutations.cancelJob.mutate(id)}
            />
          </div>
        </aside>
      </div>
    </div>
  );
}
