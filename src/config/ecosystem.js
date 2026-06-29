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
  { step: 'Research & fact-check', product: 'STUDIO', phase: 1 },
  { step: 'Script, storyboard & assets', product: 'STUDIO', phase: 1 },
  { step: 'Edit, thumbnail & SEO', product: 'STUDIO', phase: 1 },
  { step: 'Publish to OTT catalog', product: 'ORIGINALS', phase: 1 },
  { step: 'Audience watches & subscribes', product: 'ORIGINALS', phase: 1 },
  { step: 'Analytics inform next production', product: 'STUDIO', phase: 1 },
  { step: 'Proven AI modules → external SaaS', product: 'AI', phase: 2 },
  { step: 'Creators subscribe & produce globally', product: 'AI', phase: 2 },
];

/** Production pipeline inside UNTOLD STUDIO */
export const STUDIO_PIPELINE = [
  { id: 'research', label: 'Research', path: '/studio/research' },
  { id: 'script', label: 'Script', path: '/studio/scripts' },
  { id: 'storyboard', label: 'Storyboard', path: '/studio/ai' },
  { id: 'video', label: 'Video / Edit', path: '/studio/assets' },
  { id: 'thumbnail', label: 'Thumbnail', path: '/studio/ai' },
  { id: 'seo', label: 'SEO', path: '/studio/ai' },
  { id: 'publishing', label: 'Publishing', path: '/studio/content' },
  { id: 'analytics', label: 'Analytics', path: '/studio/analytics' },
];

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
