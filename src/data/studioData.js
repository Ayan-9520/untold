export const HUMAN_TEAM = [
  { role: 'Founder / Creative Director', name: 'UNTOLD Studio', bio: 'Vision, brand, and cinematic direction for every original.', icon: '🎬' },
  { role: 'Research Editor', name: 'Editorial Desk', bio: 'Deep research, source verification, and narrative structure.', icon: '📚' },
  { role: 'Script Writer', name: 'Writers Room', bio: 'Documentary scripts, narration, and episode arcs.', icon: '✍️' },
  { role: 'Video Editor', name: 'Post Production', bio: 'Cut, colour, sound — cinematic finish on every release.', icon: '🎞️' },
  { role: 'Motion Graphics Designer', name: 'Motion Lab', bio: 'Titles, maps, data viz, and premium motion design.', icon: '✨' },
  { role: 'Thumbnail Designer', name: 'Visual Studio', bio: 'High-CTR artwork and A/B tested key art.', icon: '🖼️' },
  { role: 'SEO Strategist', name: 'Growth Desk', bio: 'Discoverability, schema, and organic reach.', icon: '📈' },
  { role: 'Social Media Manager', name: 'Distribution', bio: 'Reels, shorts, and cross-platform campaigns.', icon: '📱' },
  { role: 'Full Stack Developer', name: 'Platform Engineering', bio: 'OTT platform, apps, and streaming infrastructure.', icon: '⚙️' },
  { role: 'Legal & Fact Review', name: 'Compliance', bio: 'Rights, claims, and publication standards.', icon: '⚖️' },
];

export const AI_TEAM = [
  { id: 'research', role: 'Research AI', status: 'active', tasks: 12, description: 'Gathers verified public information from reliable sources.' },
  { id: 'fact', role: 'Fact Check AI', status: 'active', tasks: 8, description: 'Verifies dates, statistics, and flags conflicting claims.' },
  { id: 'script', role: 'Script Writer AI', status: 'active', tasks: 5, description: 'Generates documentary scripts from approved research.' },
  { id: 'storyboard', role: 'Storyboard AI', status: 'idle', tasks: 2, description: 'Scene-by-scene visual plans, B-roll, and graphics.' },
  { id: 'voice', role: 'Voice AI', status: 'active', tasks: 6, description: 'Narration drafts, subtitles, and translations.' },
  { id: 'editing', role: 'Editing AI', status: 'idle', tasks: 3, description: 'Editing flow, music placement, and pacing suggestions.' },
  { id: 'thumbnail', role: 'Thumbnail AI', status: 'active', tasks: 14, description: 'Thumbnail concepts, CTR analysis, and A/B tests.' },
  { id: 'seo', role: 'SEO AI', status: 'active', tasks: 9, description: 'Titles, metadata, schema, and blog versions.' },
  { id: 'publishing', role: 'Publishing AI', status: 'scheduled', tasks: 4, description: 'Schedules releases across web and social platforms.' },
  { id: 'analytics', role: 'Analytics AI', status: 'active', tasks: 11, description: 'Watch time, retention, revenue, and traffic insights.' },
];

export const PIPELINE_STEPS = [
  'Idea',
  'Research',
  'Fact Verification',
  'Script',
  'Storyboard',
  'Voice',
  'Editing',
  'Thumbnail',
  'SEO',
  'Publishing',
  'Marketing',
  'Analytics',
];

/** In-flight documentaries across the Studio pipeline */
export const ACTIVE_PRODUCTIONS = [
  { id: 'p1', title: 'UNTOLD: Virat Kohli — The Untold Story', stage: 'research', status: 'active', assignee: 'Research Desk', sources: 142, version: 1 },
  { id: 'p2', title: 'UNTOLD: The Rise of MrBeast', stage: 'script', status: 'review', assignee: 'Writers Room', sources: 89, version: 3 },
  { id: 'p3', title: 'UNTOLD: Steve Jobs — Think Different', stage: 'script', status: 'draft', assignee: 'Writers Room', sources: 210, version: 1 },
  { id: 'p4', title: 'UNTOLD: Ronaldo — Making of a Legend', stage: 'edit', status: 'active', assignee: 'Post Production', sources: 156, version: 2 },
  { id: 'p5', title: 'UNTOLD: The AI Revolution', stage: 'publishing', status: 'scheduled', assignee: 'Growth Desk', sources: 98, version: 4 },
];
