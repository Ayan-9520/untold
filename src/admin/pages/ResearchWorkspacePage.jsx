import { useState, useEffect } from 'react';
import { Link, useParams } from 'react-router-dom';
import StudioPageHeader from '../components/StudioPageHeader';
import PipelineBar from '../components/PipelineBar';
import { studioPath } from '../../config/ecosystem';
import { useResearchByProject, useResearchMutations, useDebouncedAutosave } from '../features/research/hooks/useResearch';
import { useResearchPreferences } from '../features/research/hooks/useResearchPreferences';
import { useProjects } from '../features/projects/hooks/useProjects';
import { formatRelativeTime } from '../features/dashboard/utils';
import { studioPlatform } from '../api/adminApi';
import { RESEARCH_TOOL_TABS } from '../features/research/constants';
import TopicInputBar from '../features/research/components/TopicInputBar';
import StatisticsFactsPanel from '../features/research/components/StatisticsFactsPanel';
import ApprovalBar from '../features/research/components/ApprovalBar';
import SourceList from '../features/research/components/SourceList';
import ResearchContextSidebar from '../features/research/components/ResearchContextSidebar';
import ResearchConversationPanel from '../features/research/components/ResearchConversationPanel';
import ResearchPromptHistoryPanel from '../features/research/components/ResearchPromptHistoryPanel';
import ResearchPreviousOutputsPanel from '../features/research/components/ResearchPreviousOutputsPanel';
import ResearchPreferencesPanel from '../features/research/components/ResearchPreferencesPanel';
import ResearchProjectsPanel from '../features/research/components/ResearchProjectsPanel';

function downloadText(filename, content, mime = 'text/markdown') {
  const blob = new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

function downloadBlob(filename, blob) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

export default function ResearchWorkspacePage() {
  const { projectId } = useParams();
  const { data, isLoading, isError, refetch } = useResearchByProject(projectId);
  const { data: projectsData, isLoading: projectsLoading } = useProjects({ limit: 100 });
  const researchId = data?.workspace?.id;
  const mutations = useResearchMutations(researchId, projectId);
  const debouncedSave = useDebouncedAutosave(mutations.autosave);
  const { prefs, updatePref, resetPrefs } = useResearchPreferences();

  const [section, setSection] = useState('conversation');
  const [researchTab, setResearchTab] = useState('workspace');
  const [content, setContent] = useState('');
  const [saveStatus, setSaveStatus] = useState('saved');
  const [filteredSources, setFilteredSources] = useState(null);
  const [reusePrompt, setReusePrompt] = useState('');
  const [noteTitle, setNoteTitle] = useState('');
  const [noteContent, setNoteContent] = useState('');
  const [claim, setClaim] = useState('');
  const [comment, setComment] = useState('');
  const [tlTitle, setTlTitle] = useState('');
  const [tlDate, setTlDate] = useState('');
  const [bmTitle, setBmTitle] = useState('');
  const [bmUrl, setBmUrl] = useState('');

  useEffect(() => {
    if (data?.workspace?.workspace_content != null) {
      setContent(data.workspace.workspace_content);
    }
  }, [data?.workspace?.id, data?.workspace?.workspace_content]);

  useEffect(() => {
    setFilteredSources(null);
  }, [data?.sources]);

  const onContentChange = (val) => {
    setContent(val);
    setSaveStatus('saving');
    debouncedSave(val);
    setTimeout(() => setSaveStatus('saved'), 1600);
  };

  const slug = data?.workspace?.topic?.replace(/\s+/g, '-').slice(0, 40) || 'research';

  const handleExportMd = async () => {
    const md = await studioPlatform.exportResearchMarkdown(researchId);
    downloadText(`${slug}.md`, md);
  };

  const handleExportPdf = async () => {
    const md = await studioPlatform.exportResearchMarkdown(researchId);
    const printWin = window.open('', '_blank');
    if (printWin) {
      printWin.document.write(`<html><head><title>Research Export</title><style>body{font-family:Georgia,serif;padding:40px;line-height:1.6}pre{white-space:pre-wrap}</style></head><body><pre>${md.replace(/</g, '&lt;')}</pre></body></html>`);
      printWin.document.close();
      printWin.print();
    }
  };

  const handleExportWord = async () => {
    const blob = await studioPlatform.exportResearchWord(researchId);
    downloadBlob(`${slug}.doc`, blob);
  };

  const handleFilterSources = async (params) => {
    const items = await studioPlatform.filterResearchSources(researchId, params);
    setFilteredSources(items);
  };

  const handleRunAI = (payload) => {
    mutations.runAI.mutate(payload, {
      onSuccess: () => {
        if (prefs.autoExpandConversation) setSection('conversation');
      },
    });
  };

  const handleReusePrompt = (item) => {
    setReusePrompt(item.prompt);
    setSection('conversation');
  };

  const approvalPending = mutations.requestApproval.isPending
    || mutations.approveResearch.isPending
    || mutations.rejectResearch.isPending;

  if (isLoading) return <div className="h-96 skeleton rounded-xl" />;
  if (isError || !data) {
    return (
      <div className="text-center py-12">
        <p className="text-red-400">Research workspace unavailable</p>
        <button type="button" onClick={() => refetch()} className="text-sm text-untold-gold mt-2">Retry</button>
      </div>
    );
  }

  const { workspace, notes, sources, bookmarks, fact_checks, comments, timeline, versions, ai_history, providers } = data;
  const displaySources = filteredSources ?? sources;
  const contextCounts = {
    conversation: ai_history?.length || 0,
    references: sources?.length || 0,
    'prompt-history': ai_history?.length || 0,
    'previous-outputs': (ai_history?.length || 0) + (versions?.length || 0),
    projects: projectsData?.items?.length || 0,
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <Link to={studioPath('research')} className="text-xs text-untold-gold hover:underline">← Research hub</Link>

      <StudioPageHeader
        section="Research Studio"
        title={workspace.project_title || workspace.topic}
        description="Conversation · research · references · prompt history · outputs · preferences · projects"
      >
        <div className="flex flex-wrap gap-2 items-center">
          <span className={`text-[10px] uppercase tracking-wider ${saveStatus === 'saving' ? 'text-amber-400' : 'text-emerald-400'}`}>
            {saveStatus === 'saving' ? 'Auto-saving…' : 'Saved'}
          </span>
          <button type="button" onClick={handleExportMd} className="px-3 py-1.5 text-xs rounded-lg border dark:border-white/10 text-untold-gold">Markdown</button>
          <button type="button" onClick={handleExportPdf} className="px-3 py-1.5 text-xs rounded-lg border dark:border-white/10 text-untold-gold">PDF</button>
          <button type="button" onClick={handleExportWord} className="px-3 py-1.5 text-xs rounded-lg border dark:border-white/10 text-untold-gold">Word</button>
          <button type="button" onClick={() => mutations.saveVersion.mutate()} className="px-3 py-1.5 text-xs rounded-lg bg-untold-gold text-black font-medium">Save version</button>
        </div>
      </StudioPageHeader>

      <PipelineBar activeStep="research" />

      <TopicInputBar
        topic={workspace.topic}
        status={workspace.status}
        onSave={(topic) => mutations.updateTopic.mutate(topic)}
      />

      <ApprovalBar
        status={workspace.status}
        rejectionNotes={workspace.rejection_notes}
        pending={approvalPending}
        onRequest={() => mutations.requestApproval.mutate()}
        onApprove={() => mutations.approveResearch.mutate()}
        onReject={() => {
          const notes = window.prompt('Rejection notes (optional):');
          mutations.rejectResearch.mutate(notes || undefined);
        }}
      />

      <div className="grid lg:grid-cols-[220px_1fr] gap-6">
        <aside className="rounded-xl border dark:border-white/10 p-3 dark:bg-untold-card/20 h-fit lg:sticky lg:top-4">
          <ResearchContextSidebar active={section} onSelect={setSection} counts={contextCounts} />
        </aside>

        <div className="rounded-xl border dark:border-white/10 p-5 dark:bg-untold-card/30 min-h-[480px]">
          {section === 'conversation' && (
            <ResearchConversationPanel
              history={ai_history}
              providers={providers}
              running={mutations.runAI.isPending}
              summary={workspace.ai_summary}
              followUps={workspace.follow_up_questions}
              preferences={prefs}
              onRun={handleRunAI}
              onReusePrompt={handleReusePrompt}
              initialPrompt={reusePrompt}
            />
          )}

          {section === 'research' && (
            <div className="space-y-4">
              <div className="flex gap-1 overflow-x-auto border-b dark:border-white/10 pb-px">
                {RESEARCH_TOOL_TABS.map((tab) => (
                  <button
                    key={tab.id}
                    type="button"
                    onClick={() => setResearchTab(tab.id)}
                    className={`px-3 py-2 text-xs font-medium whitespace-nowrap border-b-2 -mb-px transition-colors ${
                      researchTab === tab.id ? 'border-untold-gold text-untold-gold' : 'border-transparent dark:text-untold-muted'
                    }`}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>

              {researchTab === 'workspace' && (
                <div className="space-y-3">
                  <p className="text-xs dark:text-untold-muted">Markdown workspace · v{workspace.content_version}</p>
                  <textarea
                    value={content}
                    onChange={(e) => onContentChange(e.target.value)}
                    rows={22}
                    className="w-full rounded-lg border dark:border-white/10 dark:bg-black/40 px-4 py-3 text-sm font-mono dark:text-white leading-relaxed resize-y"
                    placeholder="# Research notes..."
                  />
                  {workspace.ai_summary && (
                    <div className="rounded-lg border border-untold-gold/20 bg-untold-gold/5 p-4">
                      <p className="text-xs font-semibold text-untold-gold mb-2">AI Summary</p>
                      <p className="text-sm dark:text-untold-muted whitespace-pre-wrap">{workspace.ai_summary}</p>
                    </div>
                  )}
                </div>
              )}

              {researchTab === 'facts' && (
                <StatisticsFactsPanel statistics={workspace.statistics} publicFacts={workspace.public_facts} />
              )}

              {researchTab === 'notes' && (
                <div className="space-y-4">
                  <form
                    className="grid gap-2 sm:grid-cols-2"
                    onSubmit={(e) => {
                      e.preventDefault();
                      mutations.createNote.mutate({ title: noteTitle || null, content: noteContent });
                      setNoteTitle('');
                      setNoteContent('');
                    }}
                  >
                    <input value={noteTitle} onChange={(e) => setNoteTitle(e.target.value)} placeholder="Note title" className="rounded-lg border dark:border-white/10 dark:bg-black/30 px-3 py-2 text-sm dark:text-white" />
                    <input value={noteContent} onChange={(e) => setNoteContent(e.target.value)} placeholder="Note content" required className="rounded-lg border dark:border-white/10 dark:bg-black/30 px-3 py-2 text-sm dark:text-white sm:col-span-2" />
                    <button type="submit" className="px-3 py-2 text-sm rounded-lg bg-untold-gold text-black font-medium w-fit">Add note</button>
                  </form>
                  <ul className="space-y-2">
                    {notes.map((n) => (
                      <li key={n.id} className="rounded-lg border dark:border-white/10 px-3 py-2">
                        <p className="text-sm font-medium dark:text-white">{n.title || 'Untitled'}</p>
                        <p className="text-sm dark:text-untold-muted mt-1">{n.content}</p>
                        <p className="text-[10px] dark:text-untold-muted mt-1">{n.author_name} · {formatRelativeTime(n.created_at)}</p>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {researchTab === 'timeline' && (
                <div className="space-y-4">
                  <form
                    className="flex flex-wrap gap-2"
                    onSubmit={(e) => {
                      e.preventDefault();
                      mutations.addTimeline.mutate({ title: tlTitle, event_date: new Date(tlDate).toISOString(), event_type: 'milestone' });
                      setTlTitle('');
                      setTlDate('');
                    }}
                  >
                    <input type="date" value={tlDate} onChange={(e) => setTlDate(e.target.value)} required className="rounded-lg border dark:border-white/10 dark:bg-black/30 px-3 py-2 text-sm dark:text-white" />
                    <input value={tlTitle} onChange={(e) => setTlTitle(e.target.value)} placeholder="Event title" required className="flex-1 min-w-[140px] rounded-lg border dark:border-white/10 dark:bg-black/30 px-3 py-2 text-sm dark:text-white" />
                    <button type="submit" className="px-3 py-2 text-sm rounded-lg bg-untold-gold text-black font-medium">Add</button>
                  </form>
                  <ol className="relative border-l dark:border-untold-gold/30 ml-3 space-y-4">
                    {timeline.map((t) => (
                      <li key={t.id} className="ml-4">
                        <span className="absolute -left-1.5 w-3 h-3 rounded-full bg-untold-gold" />
                        <p className="text-sm dark:text-white font-medium">{t.title}</p>
                        <p className="text-xs dark:text-untold-muted">{new Date(t.event_date).toLocaleDateString()}</p>
                      </li>
                    ))}
                  </ol>
                </div>
              )}

              {researchTab === 'bookmarks' && (
                <div className="space-y-4">
                  <form
                    className="flex flex-wrap gap-2"
                    onSubmit={(e) => {
                      e.preventDefault();
                      mutations.addBookmark.mutate({ title: bmTitle, url: bmUrl || null });
                      setBmTitle('');
                      setBmUrl('');
                    }}
                  >
                    <input value={bmTitle} onChange={(e) => setBmTitle(e.target.value)} placeholder="Bookmark title" required className="flex-1 rounded-lg border dark:border-white/10 dark:bg-black/30 px-3 py-2 text-sm dark:text-white" />
                    <input value={bmUrl} onChange={(e) => setBmUrl(e.target.value)} placeholder="URL" className="flex-1 rounded-lg border dark:border-white/10 dark:bg-black/30 px-3 py-2 text-sm dark:text-white" />
                    <button type="submit" className="px-3 py-2 text-sm rounded-lg bg-untold-gold text-black font-medium">Bookmark</button>
                  </form>
                  <ul className="space-y-2">
                    {bookmarks.map((b) => (
                      <li key={b.id} className="rounded-lg border border-untold-gold/20 bg-untold-gold/5 px-3 py-2">
                        {b.url ? <a href={b.url} className="text-sm text-untold-gold" target="_blank" rel="noreferrer">{b.title}</a> : <p className="text-sm dark:text-white">{b.title}</p>}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {researchTab === 'fact-check' && (
                <div className="space-y-4">
                  <form
                    onSubmit={(e) => {
                      e.preventDefault();
                      mutations.addFactCheck.mutate({ claim });
                      setClaim('');
                    }}
                    className="flex gap-2"
                  >
                    <input value={claim} onChange={(e) => setClaim(e.target.value)} placeholder="Claim to verify" required className="flex-1 rounded-lg border dark:border-white/10 dark:bg-black/30 px-3 py-2 text-sm dark:text-white" />
                    <button type="submit" className="px-3 py-2 text-sm rounded-lg bg-untold-gold text-black font-medium">Add</button>
                  </form>
                  <ul className="space-y-2">
                    {fact_checks.map((fc) => (
                      <li key={fc.id} className="rounded-lg border dark:border-white/10 px-3 py-2 flex justify-between gap-3">
                        <p className="text-sm dark:text-white flex-1">{fc.claim}</p>
                        <select
                          value={fc.status}
                          onChange={(e) => mutations.updateFactCheck.mutate({ id: fc.id, data: { status: e.target.value } })}
                          className="text-xs rounded border dark:border-white/10 dark:bg-black/30 px-2 py-1 dark:text-white capitalize"
                        >
                          {['pending', 'verified', 'disputed', 'rejected'].map((s) => <option key={s} value={s}>{s}</option>)}
                        </select>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {researchTab === 'comments' && (
                <div className="space-y-4">
                  <form
                    onSubmit={(e) => { e.preventDefault(); mutations.addComment.mutate(comment); setComment(''); }}
                    className="flex gap-2"
                  >
                    <input value={comment} onChange={(e) => setComment(e.target.value)} placeholder="Team comment" required className="flex-1 rounded-lg border dark:border-white/10 dark:bg-black/30 px-3 py-2 text-sm dark:text-white" />
                    <button type="submit" className="px-3 py-2 text-sm rounded-lg bg-untold-gold text-black font-medium">Post</button>
                  </form>
                  <ul className="space-y-2">
                    {comments.map((c) => (
                      <li key={c.id} className="rounded-lg border dark:border-white/10 px-3 py-2">
                        <p className="text-sm dark:text-white">{c.content}</p>
                        <p className="text-[10px] dark:text-untold-muted mt-1">{c.author_name} · {formatRelativeTime(c.created_at)}</p>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {researchTab === 'versions' && (
                <ul className="space-y-2">
                  {versions.map((v) => (
                    <li key={v.id} className="flex items-center justify-between gap-3 rounded-lg border dark:border-white/10 px-3 py-2">
                      <div>
                        <p className="text-sm dark:text-white">Version {v.version}</p>
                        <p className="text-[10px] dark:text-untold-muted">{v.author_name} · {formatRelativeTime(v.created_at)}</p>
                      </div>
                      <button type="button" onClick={() => mutations.restoreVersion.mutate(v.id)} className="text-xs text-untold-gold hover:underline">Restore</button>
                    </li>
                  ))}
                  {versions.length === 0 && <p className="text-sm dark:text-untold-muted text-center py-8">No saved versions yet</p>}
                </ul>
              )}
            </div>
          )}

          {section === 'references' && (
            <SourceList
              sources={displaySources}
              onAdd={(sourceData) => mutations.addSource.mutate(sourceData)}
              onFilter={handleFilterSources}
            />
          )}

          {section === 'prompt-history' && (
            <ResearchPromptHistoryPanel history={ai_history} onReuse={handleReusePrompt} />
          )}

          {section === 'previous-outputs' && (
            <ResearchPreviousOutputsPanel history={ai_history} versions={versions} />
          )}

          {section === 'preferences' && (
            <ResearchPreferencesPanel
              prefs={prefs}
              providers={providers}
              onChange={updatePref}
              onReset={resetPrefs}
            />
          )}

          {section === 'projects' && (
            <ResearchProjectsPanel
              projects={projectsData?.items}
              activeProjectId={projectId}
              loading={projectsLoading}
            />
          )}
        </div>
      </div>
    </div>
  );
}
