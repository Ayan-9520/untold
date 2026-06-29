import { useState, useEffect } from 'react';
import { aiPipeline } from '../api/adminApi';
import { AI_LOCALIZATION_LANGUAGES, AI_PIPELINE_STEPS } from '../../data/contentPillars';
import StatCard from '../components/StatCard';
import Modal from '../components/Modal';
import { FilmIcon } from '../components/AdminIcons';

const MOCK_JOBS = [
  {
    id: 1,
    video_title: 'Dhoni: The Untold Captain',
    source_language: 'en',
    target_languages: ['hi', 'es', 'ru', 'ar'],
    status: 'completed',
    progress: 100,
    steps: AI_PIPELINE_STEPS.map((s) => ({ ...s, status: 'completed' })),
    created_at: new Date(Date.now() - 86400000).toISOString(),
  },
  {
    id: 2,
    video_title: 'Messi vs Ronaldo: Eternal Rivalry',
    source_language: 'en',
    target_languages: ['hi', 'es', 'ru'],
    status: 'processing',
    progress: 58,
    steps: AI_PIPELINE_STEPS.map((s, i) => ({
      ...s,
      status: i < 3 ? 'completed' : i === 3 ? 'processing' : 'pending',
    })),
    created_at: new Date().toISOString(),
  },
];

function StepStatus({ status }) {
  const colors = {
    completed: 'text-green-400',
    processing: 'text-untold-gold animate-pulse',
    pending: 'dark:text-untold-muted light:text-gray-400',
    failed: 'text-red-400',
  };
  return <span className={`text-xs capitalize ${colors[status] || colors.pending}`}>{status}</span>;
}

export default function AILocalizationPage() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [usingMock, setUsingMock] = useState(false);
  const [selected, setSelected] = useState(null);

  const fetchJobs = () => {
    setLoading(true);
    aiPipeline.listJobs()
      .then((data) => {
        const items = data.items?.length ? data.items : MOCK_JOBS;
        setJobs(items);
        setUsingMock(!data.items?.length);
      })
      .catch(() => { setJobs(MOCK_JOBS); setUsingMock(true); })
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchJobs(); }, []);

  const completed = jobs.filter((j) => j.status === 'completed').length;
  const processing = jobs.filter((j) => j.status === 'processing').length;

  return (
    <div className="space-y-8 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold dark:text-untold-white light:text-black">AI Localization</h1>
        <p className="text-sm dark:text-untold-muted light:text-gray-500 mt-1">
          Upload once → AI distributes globally. Speech-to-text, translation, subtitles, dubbing.
        </p>
      </div>

      {usingMock && (
        <p className="text-xs px-3 py-2 rounded-lg bg-amber-500/10 text-amber-300 border border-amber-500/20">
          Showing demo localization jobs — API pipeline not connected yet.
        </p>
      )}

      <div className="grid sm:grid-cols-3 gap-4">
        <StatCard title="Total Jobs" value={jobs.length} icon={FilmIcon} accent="gold" />
        <StatCard title="Processing" value={processing} icon={FilmIcon} accent="blue" />
        <StatCard title="Completed" value={completed} icon={FilmIcon} accent="green" />
      </div>

      <div className="rounded-xl border dark:border-white/10 light:border-gray-200 p-5">
        <h2 className="text-sm font-semibold dark:text-untold-white light:text-black mb-3">Supported Languages</h2>
        <div className="flex flex-wrap gap-2">
          {AI_LOCALIZATION_LANGUAGES.map((lang) => (
            <span
              key={lang.code}
              className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-sm
                dark:bg-white/5 light:bg-gray-100 dark:text-untold-white light:text-black"
            >
              {lang.flag} {lang.label}
              {lang.rtl && <span className="text-[10px] text-untold-gold">RTL</span>}
            </span>
          ))}
        </div>
      </div>

      <div className="rounded-xl border dark:border-white/10 light:border-gray-200 overflow-hidden">
        <div className="px-5 py-4 border-b dark:border-white/10 light:border-gray-200">
          <h2 className="font-semibold dark:text-untold-white light:text-black">Localization Jobs</h2>
        </div>
        {loading ? (
          <div className="h-48 skeleton" />
        ) : (
          <div className="divide-y dark:divide-white/10 light:divide-gray-200">
            {jobs.map((job) => (
              <button
                key={job.id}
                type="button"
                onClick={() => setSelected(job)}
                className="w-full text-left px-5 py-4 hover:dark:bg-white/5 hover:light:bg-gray-50 transition-colors"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div>
                    <p className="font-medium dark:text-untold-white light:text-black">{job.video_title}</p>
                    <p className="text-xs dark:text-untold-muted light:text-gray-500 mt-1">
                      {job.source_language?.toUpperCase()} → {job.target_languages?.join(', ').toUpperCase()}
                    </p>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="w-32 h-2 rounded-full dark:bg-white/10 light:bg-gray-200 overflow-hidden">
                      <div
                        className="h-full bg-untold-gold transition-all"
                        style={{ width: `${job.progress || 0}%` }}
                      />
                    </div>
                    <span className={`text-xs font-semibold uppercase
                      ${job.status === 'completed' ? 'text-green-400' : job.status === 'processing' ? 'text-untold-gold' : 'dark:text-untold-muted'}`}>
                      {job.status}
                    </span>
                  </div>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>

      <Modal open={!!selected} onClose={() => setSelected(null)} title="Pipeline Progress" wide>
        {selected && (
          <div className="space-y-4">
            <p className="text-sm dark:text-untold-muted light:text-gray-500">{selected.video_title}</p>
            <div className="space-y-3">
              {(selected.steps || AI_PIPELINE_STEPS).map((step, i) => (
                <div key={step.id || i} className="flex items-center justify-between py-2 border-b dark:border-white/5 last:border-0">
                  <span className="text-sm dark:text-untold-white light:text-black">{step.label || step.id}</span>
                  <StepStatus status={step.status || 'pending'} />
                </div>
              ))}
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
