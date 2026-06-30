/**
 * UNTOLD three-product ecosystem — single source of truth.
 *
 * ORIGINALS  → public OTT (what viewers see)
 * STUDIO     → internal production OS (team only)
 * AI         → future SaaS (Phase 2 — external creators)
 */

export const PRODUCTS = {
  ORIGINALS: {
    id: 'originals',
    name: 'UNTOLD ORIGINALS',
    shortName: 'Originals',
    tagline: 'The Story Behind The Glory',
    description: 'Netflix-style documentary streaming for the world.',
    basePath: '/',
    audience: 'public',
    phase: 1,
    color: 'gold',
    role: 'Revenue & audience — what subscribers see',
  },
  STUDIO: {
    id: 'studio',
    name: 'UNTOLD STUDIO',
    shortName: 'Studio',
    tagline: 'Production OS · Internal only',
    description: 'Research through publishing — your media company operating system.',
    basePath: '/studio',
    loginPath: '/studio/login',
    audience: 'internal',
    phase: 1,
    color: 'blue',
    role: 'Production engine — research, AI, edit, publish',
  },
  AI: {
    id: 'ai',
    name: 'UNTOLD AI',
    shortName: 'AI',
    tagline: 'Creator workflow SaaS',
    description: 'Research, script, storyboard, thumbnails, SEO, and publishing AI for creators and agencies.',
    basePath: '/ai',
    audience: 'saas',
    phase: 2,
    color: 'purple',
    role: 'External SaaS — proven Studio tools for creators',
  },
};

/** Phases 1–23 — Studio product features (shipped) */
export const STUDIO_FEATURE_PHASES = [
  { id: 1, label: 'OTT catalog & content API', done: true },
  { id: 2, label: 'User auth & subscriptions', done: true },
  { id: 3, label: 'News & live engine', done: true },
  { id: 4, label: 'Monetization & revenue', done: true },
  { id: 5, label: 'Studio platform core', done: true },
  { id: 6, label: 'Studio auth & RBAC', done: true },
  { id: 7, label: 'Project management', done: true, path: '/studio/projects' },
  { id: 8, label: 'Research studio', done: true, path: '/studio/research' },
  { id: 9, label: 'Script studio', done: true, path: '/studio/scripts' },
  { id: 10, label: 'Storyboard studio', done: true, path: '/studio/storyboard' },
  { id: 11, label: 'Image studio', done: true, path: '/studio/images' },
  { id: 12, label: 'Video studio', done: true, path: '/studio/videos' },
  { id: 13, label: 'Voice studio', done: true, path: '/studio/voice' },
  { id: 14, label: 'Music studio', done: true, path: '/studio/music' },
  { id: 15, label: 'Timeline editor', done: true, path: '/studio/timeline' },
  { id: 16, label: 'Asset library', done: true, path: '/studio/assets' },
  { id: 17, label: 'SEO & shorts studio', done: true, path: '/studio/seo' },
  { id: 18, label: 'Translation studio', done: true, path: '/studio/translation' },
  { id: 19, label: 'AI studio command', done: true, path: '/studio/ai' },
  { id: 20, label: 'Publishing CMS', done: true, path: '/studio/content' },
  { id: 21, label: 'Publishing agent', done: true, path: '/studio/publishing-agent' },
  { id: 22, label: 'Workflow engine', done: true, path: '/studio/pipeline' },
  { id: 23, label: 'Studio analytics & admin', done: true, path: '/studio/analytics' },
];

/** Phases 24–37 — AI platform layers */
export const AI_PLATFORM_PHASES = [
  { id: 24, label: 'AI Core', done: true, path: '/studio/ai', description: 'Module registry, job queue, provider abstraction' },
  { id: 25, label: 'LLM Provider', done: true, path: '/studio/ai', description: 'OpenAI, Gemini, Anthropic, demo fallback' },
  { id: 26, label: 'Image Provider', done: true, path: '/studio/images', description: 'Multi-vendor image generation registry' },
  { id: 27, label: 'Video Provider', done: true, path: '/studio/videos', description: 'B-roll, highlights, motion graphics' },
  { id: 28, label: 'Voice Provider', done: true, path: '/studio/voice', description: 'TTS narration & voice cloning bridge' },
  { id: 29, label: 'Music Provider', done: true, path: '/studio/music', description: 'Score generation & stem previews' },
  { id: 30, label: 'Translation Provider', done: true, path: '/studio/translation', description: 'Google, DeepL, OpenAI, Azure, AWS' },
  { id: 31, label: 'Embeddings', done: true, path: '/studio/ai', description: 'OpenAI, Voyage, Cohere, Gemini, Jina, BGE' },
  { id: 32, label: 'Vector Database', done: true, path: '/studio/ai', description: 'pgvector, Pinecone, Weaviate, Qdrant, Milvus, Chroma' },
  { id: 33, label: 'AI Orchestrator', done: true, path: '/studio/pipeline', description: 'Idea → Analytics workflow engine' },
  { id: 34, label: 'Agent Framework', done: true, path: '/studio/pipeline', description: '13 chained production agents' },
  { id: 35, label: 'Prompt Library', done: true, path: '/studio/ai', description: 'Per-module templates & workflow prompts' },
  { id: 36, label: 'AI Memory', done: true, path: '/studio/research', description: 'Conversation, TM, references, prompt history' },
  { id: 37, label: 'AI Audit & Observability', done: true, path: '/studio/ai', description: 'Tokens, latency, cost, failures, telemetry' },
];

/** Full platform roadmap — Phases 1–37 */
export const PLATFORM_ROADMAP = [
  {
    type: 'group',
    id: 'studio-features',
    from: 1,
    to: 23,
    label: 'Studio Features',
    done: true,
    phases: STUDIO_FEATURE_PHASES,
  },
  ...AI_PLATFORM_PHASES.map((p) => ({ type: 'phase', ...p })),
];

/** Roadmap phases */
export const PHASES = {
  1: {
    id: 1,
    name: 'Phase 1',
    title: 'Build & Prove',
    status: 'active',
    tagline: 'Originals + Studio together',
    goal: 'Ship the OTT and run every documentary through Studio before it hits subscribers.',
    products: ['ORIGINALS', 'STUDIO'],
    timeline: 'Now',
    milestones: [
      { label: 'Launch UNTOLD ORIGINALS OTT', done: true },
      { label: 'Research → Script → Assets pipeline in Studio', done: true },
      { label: 'AI agents for storyboard, thumbnails, SEO', done: true },
      { label: 'Publish from Studio CMS → Originals catalog', done: true },
      { label: 'Viewer analytics & revenue feed back to Studio', done: true },
    ],
  },
  2: {
    id: 2,
    name: 'Phase 2',
    title: 'Scale AI SaaS',
    status: 'planned',
    tagline: 'UNTOLD AI for external creators',
    goal: 'Extract battle-tested Studio AI into a subscription product for YouTubers, agencies, and universities.',
    products: ['AI'],
    timeline: 'Next',
    milestones: [
      { label: 'UNTOLD AI landing & waitlist at /ai', done: true },
      { label: 'Research & Script AI public beta', done: false },
      { label: 'Thumbnail, SEO, Publishing automation tiers', done: false },
      { label: 'Team seats & Business plan', done: false },
      { label: 'API access & Enterprise licensing', done: false },
    ],
  },
};

/** How products connect (arrows on ecosystem map) */
export const ECOSYSTEM_CONNECTIONS = [
  { from: 'STUDIO', to: 'ORIGINALS', label: 'Publish documentaries', phase: 1 },
  { from: 'ORIGINALS', to: 'STUDIO', label: 'Views, subs & revenue data', phase: 1 },
  { from: 'STUDIO', to: 'AI', label: 'Mature AI modules → SaaS', phase: 2 },
  { from: 'AI', to: 'STUDIO', label: 'Dogfood before external launch', phase: 2, internal: true },
];

/** End-to-end content lifecycle */
export const ECOSYSTEM_FLOW = [
  { step: 'Idea & project brief', product: 'STUDIO', phase: 1 },
  { step: 'AI research, script & storyboard', product: 'STUDIO', phase: 1 },
  { step: 'AI images, video, voice & music', product: 'STUDIO', phase: 1 },
  { step: 'Timeline edit & assembly', product: 'STUDIO', phase: 1 },
  { step: 'AI SEO, translation & publishing', product: 'STUDIO', phase: 1 },
  { step: 'Publish to OTT catalog', product: 'ORIGINALS', phase: 1 },
  { step: 'Audience watches & subscribes', product: 'ORIGINALS', phase: 1 },
  { step: 'Analytics inform next production', product: 'STUDIO', phase: 1 },
  { step: 'Proven AI modules → external SaaS', product: 'AI', phase: 2 },
  { step: 'Creators subscribe & produce globally', product: 'AI', phase: 2 },
];

/** End-to-end studio production: Idea → Analytics */
export const STUDIO_PRODUCTION_PIPELINE = [
  { id: 'idea', label: 'Idea', path: '/studio/projects' },
  { id: 'research', label: 'AI Research', path: '/studio/research' },
  { id: 'script', label: 'AI Script', path: '/studio/scripts' },
  { id: 'storyboard', label: 'AI Storyboard', path: '/studio/storyboard' },
  { id: 'image', label: 'AI Images', path: '/studio/images' },
  { id: 'video', label: 'AI Video Clips', path: '/studio/videos' },
  { id: 'voice', label: 'AI Voice', path: '/studio/voice' },
  { id: 'music', label: 'AI Music', path: '/studio/music' },
  { id: 'timeline', label: 'Timeline Editor', path: '/studio/timeline' },
  { id: 'seo', label: 'AI SEO', path: '/studio/seo' },
  { id: 'translation', label: 'AI Translation', path: '/studio/translation' },
  { id: 'publisher', label: 'Publishing', path: '/studio/publishing-agent' },
  { id: 'analytics', label: 'Analytics', path: '/studio/analytics' },
];

/** Workflow Engine agents — same chain as production pipeline */
export const WORKFLOW_AGENTS = STUDIO_PRODUCTION_PIPELINE.map(({ id, label, path }) => ({
  id,
  label,
  path,
}));

/** Core pipeline shown on studio pages */
export const STUDIO_CORE_PIPELINE = STUDIO_PRODUCTION_PIPELINE;

/** Optional ops steps appended when `extended` is set on PipelineBar */
export const STUDIO_PIPELINE_EXTENDED = [
  { id: 'assets', label: 'Asset Library', path: '/studio/assets' },
  { id: 'content', label: 'Publishing CMS', path: '/studio/content' },
];

/** Production pipeline inside UNTOLD STUDIO */
export const STUDIO_PIPELINE = STUDIO_PRODUCTION_PIPELINE;

/** AI modules — internal (Studio) today, external (AI SaaS) in Phase 2 */
export const AI_MODULES = [
  { id: 'research', name: 'Research AI', desc: 'Timelines, biographies, sources, and verified statistics.', phase: 1, studio: true, saas: true },
  { id: 'script', name: 'Script AI', desc: 'Full documentary scripts from your research folder.', phase: 1, studio: true, saas: true },
  { id: 'storyboard', name: 'Storyboard AI', desc: 'Scene plans — drone shots, maps, graphs, narration beats.', phase: 1, studio: true, saas: true },
  { id: 'thumbnail', name: 'Thumbnail AI', desc: '20 concepts with CTR prediction from your script.', phase: 1, studio: true, saas: true },
  { id: 'seo', name: 'SEO AI', desc: 'Titles, tags, schema, blogs, and internal links.', phase: 1, studio: true, saas: true },
  { id: 'publishing', name: 'Publishing AI', desc: 'YouTube, Instagram, TikTok, web — one workflow.', phase: 1, studio: true, saas: true },
  { id: 'shorts', name: 'Shorts AI', desc: 'Turn a 60-min doc into shorts, reels, clips, and newsletter.', phase: 2, studio: true, saas: true },
  { id: 'analytics', name: 'Analytics AI', desc: 'Views, retention, revenue — and what to produce next.', phase: 2, studio: true, saas: true },
];

export const AI_SAAS_PLANS = [
  { id: 'free', name: 'Free', price: '$0', features: ['Limited research queries', 'Script drafts', 'Watermark exports'] },
  { id: 'pro', name: 'Pro', price: '$49/mo', features: ['Unlimited research', 'Full script AI', 'Thumbnail concepts', 'SEO pack'] },
  { id: 'business', name: 'Business', price: '$199/mo', features: ['Team seats', 'Publishing automation', 'Shorts from long-form', 'Priority support'] },
  { id: 'enterprise', name: 'Enterprise', price: 'Custom', features: ['API access', 'White-label', 'Enterprise licensing', 'Dedicated success'] },
];

/** Revenue flywheel — how the ecosystem compounds */
export const REVENUE_FLYWHEEL = [
  { step: 'Studio produces premium docs', product: 'STUDIO' },
  { step: 'Originals drives subscriptions & ads', product: 'ORIGINALS' },
  { step: 'Data guides what to make next', product: 'STUDIO' },
  { step: 'AI tools reduce cost per documentary', product: 'STUDIO' },
  { step: 'SaaS revenue funds more Originals', product: 'AI' },
];

export function studioPath(segment = '') {
  const base = PRODUCTS.STUDIO.basePath;
  return segment ? `${base}/${segment.replace(/^\//, '')}` : base;
}

export function aiPath(segment = '') {
  const base = PRODUCTS.AI.basePath;
  return segment ? `${base}/${segment.replace(/^\//, '')}` : base;
}

export function getPhase(id) {
  return PHASES[id] ?? null;
}

export function productsInPhase(phaseId) {
  return Object.entries(PRODUCTS)
    .filter(([, p]) => p.phase === phaseId)
    .map(([key]) => key);
}
