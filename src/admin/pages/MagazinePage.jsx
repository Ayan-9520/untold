import { useState, useEffect } from 'react';
import StatCard from '../components/StatCard';
import Modal from '../components/Modal';
import Chip from '../../components/ui/Chip';
import Badge from '../../components/ui/Badge';
import {
  MAGAZINE_WORKFLOW_STEPS,
  MAGAZINE_THEMES,
  MAGAZINE_AI_STACK,
  MAGAZINE_SECTIONS,
  MOCK_WORKFLOW_JOBS,
  getMagazineIssues,
} from '../../data/magazineCatalog';
import { FilmIcon } from '../components/AdminIcons';

const STATUS_COLORS = {
  completed: 'text-green-400',
  processing: 'text-untold-gold animate-pulse',
  pending: 'dark:text-untold-muted light:text-gray-400',
};

export default function MagazinePage() {
  const [jobs, setJobs] = useState([]);
  const [usingMock, setUsingMock] = useState(false);
  const [theme, setTheme] = useState('IPL Special');
  const [quarter, setQuarter] = useState('Q2');
  const [year, setYear] = useState(2026);
  const [generating, setGenerating] = useState(false);
  const [selectedJob, setSelectedJob] = useState(null);
  const issues = getMagazineIssues();

  useEffect(() => {
    import('../api/adminApi').then((m) => {
      m.magazine?.listJobs?.()
        .then((data) => {
          const items = data.items?.length ? data.items : MOCK_WORKFLOW_JOBS;
          setJobs(items);
          setUsingMock(!data.items?.length);
        })
        .catch(() => { setJobs(MOCK_WORKFLOW_JOBS); setUsingMock(true); });
    });
  }, []);

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      const adminApi = await import('../api/adminApi');
      if (adminApi.magazine?.generateIssue) {
        const job = await adminApi.magazine.generateIssue({ theme, quarter, year });
        setJobs((prev) => [job, ...prev]);
      } else {
        const newJob = {
          id: `job-${Date.now()}`,
          theme,
          quarter,
          year,
          status: 'collecting',
          progress: 5,
          steps: MAGAZINE_WORKFLOW_STEPS.map((s, i) => ({
            ...s,
            status: i === 0 ? 'processing' : 'pending',
          })),
          createdAt: new Date().toISOString(),
        };
        setJobs((prev) => [newJob, ...prev]);
      }
    } finally {
      setGenerating(false);
    }
  };

  const handleApprove = async (jobId) => {
    const adminApi = await import('../api/adminApi');
    await adminApi.magazine?.approveIssue?.(jobId).catch(() => {});
    setJobs((prev) =>
      prev.map((j) =>
        j.id === jobId
          ? { ...j, status: 'ready', progress: 100, steps: j.steps?.map((s) => ({ ...s, status: 'completed' })) }
          : j
      )
    );
    setSelectedJob(null);
  };

  return (
    <div className="space-y-8 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold dark:text-untold-white light:text-black">Magazine Editor AI</h1>
        <p className="text-sm dark:text-untold-muted light:text-gray-500 mt-1">
          UNTOLD E-Magazine — Data → Editorial → Design → Publish (85–90% automated)
        </p>
      </div>

      {usingMock && (
        <p className="text-xs px-3 py-2 rounded-lg bg-amber-500/10 text-amber-300 border border-amber-500/20">
          Showing demo magazine workflow — connect backend for live editorial jobs.
        </p>
      )}

      <div className="grid sm:grid-cols-3 gap-4">
        <StatCard title="Published Issues" value={issues.length} icon={FilmIcon} accent="gold" />
        <StatCard title="Active Jobs" value={jobs.filter((j) => j.status !== 'ready').length} icon={FilmIcon} accent="blue" />
        <StatCard title="Automation" value="87%" icon={FilmIcon} accent="green" />
      </div>

      <div className="rounded-xl border dark:border-white/10 light:border-gray-200 p-6">
        <h2 className="font-semibold dark:text-untold-white light:text-black mb-4">Generate E-Magazine Issue</h2>
        <div className="grid sm:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="text-xs dark:text-untold-muted mb-1 block">Theme</label>
            <select
              value={theme}
              onChange={(e) => setTheme(e.target.value)}
              className="w-full rounded-lg px-3 py-2 text-sm dark:bg-untold-dark dark:border-white/10 border"
            >
              {MAGAZINE_THEMES.map((t) => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>
          <div>
            <label className="text-xs dark:text-untold-muted mb-1 block">Quarter</label>
            <div className="flex gap-2">
              {['Q1', 'Q2', 'Q3', 'Q4'].map((q) => (
                <Chip key={q} active={quarter === q} onClick={() => setQuarter(q)}>{q}</Chip>
              ))}
            </div>
          </div>
          <div>
            <label className="text-xs dark:text-untold-muted mb-1 block">Year</label>
            <input
              type="number"
              value={year}
              onChange={(e) => setYear(Number(e.target.value))}
              className="w-full rounded-lg px-3 py-2 text-sm dark:bg-untold-dark dark:border-white/10 border"
            />
          </div>
        </div>
        <p className="text-xs dark:text-untold-muted mb-4">
          Sections: {MAGAZINE_SECTIONS.map((s) => s.label).join(' · ')}
        </p>
        <button
          type="button"
          onClick={handleGenerate}
          disabled={generating}
          className="px-5 py-2.5 rounded-lg bg-untold-gold text-untold-dark text-sm font-semibold disabled:opacity-60"
        >
          {generating ? 'Starting agents…' : 'Generate Issue'}
        </button>
      </div>

      <div className="rounded-xl border dark:border-white/10 light:border-gray-200 p-5">
        <h2 className="font-semibold dark:text-untold-white light:text-black mb-3">AI Tools Stack</h2>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3 text-sm">
          <div><span className="text-untold-gold font-semibold">Writing:</span> {MAGAZINE_AI_STACK.writing.join(', ')}</div>
          <div><span className="text-untold-gold font-semibold">Design:</span> {MAGAZINE_AI_STACK.design.join(', ')}</div>
          <div><span className="text-untold-gold font-semibold">Publish:</span> {MAGAZINE_AI_STACK.publishing.join(', ')}</div>
          <div><span className="text-untold-gold font-semibold">Automation:</span> {MAGAZINE_AI_STACK.automation.join(', ')}</div>
        </div>
      </div>

      <div className="rounded-xl border dark:border-white/10 light:border-gray-200 overflow-hidden">
        <div className="px-5 py-4 border-b dark:border-white/10">
          <h2 className="font-semibold dark:text-untold-white light:text-black">Workflow Jobs</h2>
        </div>
        <div className="divide-y dark:divide-white/10">
          {jobs.map((job) => (
            <button
              key={job.id}
              type="button"
              onClick={() => setSelectedJob(job)}
              className="w-full text-left px-5 py-4 hover:dark:bg-white/5 transition-colors"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div>
                  <p className="font-medium dark:text-untold-white light:text-black">{job.theme} · {job.quarter} {job.year}</p>
                  <p className="text-xs dark:text-untold-muted mt-1 capitalize">Status: {job.status}</p>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-32 h-2 rounded-full dark:bg-white/10 overflow-hidden">
                    <div className="h-full bg-untold-gold" style={{ width: `${job.progress || 0}%` }} />
                  </div>
                  <Badge variant={job.status === 'ready' ? 'gold' : 'outline'} size="sm">{job.progress || 0}%</Badge>
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>

      <Modal open={!!selectedJob} onClose={() => setSelectedJob(null)} title="Magazine Workflow" wide>
        {selectedJob && (
          <div className="space-y-4">
            <p className="text-sm dark:text-untold-muted">{selectedJob.theme} — {selectedJob.quarter} {selectedJob.year}</p>
            <div className="space-y-2">
              {(selectedJob.steps || MAGAZINE_WORKFLOW_STEPS).map((step) => (
                <div key={step.id} className="flex justify-between py-2 border-b dark:border-white/5 last:border-0">
                  <div>
                    <p className="text-sm dark:text-untold-white light:text-black">{step.label}</p>
                    <p className="text-xs dark:text-untold-muted">{step.agent}</p>
                  </div>
                  <span className={`text-xs capitalize ${STATUS_COLORS[step.status] || STATUS_COLORS.pending}`}>
                    {step.status || 'pending'}
                  </span>
                </div>
              ))}
            </div>
            {selectedJob.status !== 'ready' && (
              <button
                type="button"
                onClick={() => handleApprove(selectedJob.id)}
                className="w-full py-2.5 rounded-lg bg-untold-gold text-untold-dark font-semibold text-sm"
              >
                Approve & Publish (Editor-in-Chief)
              </button>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
}
