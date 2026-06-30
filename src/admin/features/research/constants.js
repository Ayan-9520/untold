export const AI_ACTIONS = [
  { id: 'full_research', label: 'Full research', icon: '🔍' },
  { id: 'summary', label: 'AI summary', icon: '📝' },
  { id: 'timeline', label: 'Timeline', icon: '📅' },
  { id: 'statistics', label: 'Statistics', icon: '📊' },
  { id: 'public_facts', label: 'Public facts', icon: '✅' },
  { id: 'follow_up', label: 'Follow-up Qs', icon: '❓' },
  { id: 'fact_check', label: 'Fact check', icon: '🛡️' },
];

export const RESEARCH_CONTEXT_SECTIONS = [
  { id: 'conversation', label: 'Conversation' },
  { id: 'research', label: 'Research' },
  { id: 'references', label: 'References' },
  { id: 'prompt-history', label: 'Prompt History' },
  { id: 'previous-outputs', label: 'Previous Outputs' },
  { id: 'preferences', label: 'User Preferences' },
  { id: 'projects', label: 'Projects' },
];

export const RESEARCH_TOOL_TABS = [
  { id: 'workspace', label: 'Workspace' },
  { id: 'facts', label: 'Stats & Facts' },
  { id: 'notes', label: 'Notes' },
  { id: 'timeline', label: 'Timeline' },
  { id: 'bookmarks', label: 'Bookmarks' },
  { id: 'fact-check', label: 'Fact Check' },
  { id: 'comments', label: 'Comments' },
  { id: 'versions', label: 'Versions' },
];

export const SOURCE_TYPES = ['article', 'book', 'interview', 'video', 'archive', 'statistics'];

export const DEFAULT_RESEARCH_PREFERENCES = {
  defaultProvider: '',
  defaultAction: 'full_research',
  autoExpandConversation: true,
  showFollowUps: true,
};
