/**
 * UNTOLD E-Magazine — premium sports e-magazine catalog
 * AI workflow: Data → Editorial → Design → Publish (85–90% automated)
 */

export const MAGAZINE_BRAND = {
  name: 'UNTOLD E-Magazine',
  tagline: 'The Story Behind The Glory',
  frequency: '4 editions per year',
  editionsPerYear: 4,
};

export const MAGAZINE_SECTIONS = [
  { id: 'cover-story', label: 'Cover Story' },
  { id: 'editorial', label: 'Editorial' },
  { id: 'originals', label: 'Originals' },
  { id: 'legends', label: 'Legends' },
  { id: 'rivalries', label: 'Rivalries' },
  { id: 'events', label: 'Events' },
  { id: 'stats', label: 'Stats & Analytics' },
  { id: 'trends', label: 'Global Sports Trends' },
];

export const MAGAZINE_WORKFLOW_STEPS = [
  { id: 'collecting', label: 'Collecting Data', agent: 'Data Collection Agent' },
  { id: 'writing', label: 'Writing', agent: 'Editorial AI Agent' },
  { id: 'designing', label: 'Designing', agent: 'Design AI Agent' },
  { id: 'publishing', label: 'Publishing', agent: 'Publishing Agent' },
  { id: 'ready', label: 'Ready', agent: 'Editor-in-Chief Approval' },
];

export const MAGAZINE_AI_STACK = {
  writing: ['OpenAI', 'Claude'],
  design: ['Canva', 'Adobe Firefly'],
  publishing: ['Issuu', 'Flipsnack'],
  automation: ['n8n'],
};

export const MAGAZINE_ACCESS = {
  free: { label: 'Free Sample', priceINR: 0, priceUSD: 0 },
  single: { label: 'Single Issue', priceINRMin: 49, priceINRMax: 199, priceUSD: 2.99 },
  premium: { label: 'Premium Membership', included: true },
  vip: { label: 'VIP Membership', included: true },
};

export const MAGAZINE_THEMES = [
  'World Cup Special',
  'Olympics Special',
  'IPL Special',
  'Champions League',
  'Grand Slam',
  'General Edition',
];

function issue(
  id,
  title,
  quarter,
  year,
  theme,
  coverImage,
  opts = {}
) {
  return {
    id,
    title,
    quarter,
    year,
    theme,
    coverImage,
    tagline: opts.tagline || MAGAZINE_BRAND.tagline,
    status: opts.status || 'published',
    access: opts.access || 'paid',
    priceINR: opts.priceINR ?? 99,
    priceUSD: opts.priceUSD ?? 2.99,
    pageCount: opts.pageCount ?? 48,
    publishedAt: opts.publishedAt || `${year}-${quarter === 'Q1' ? '03' : quarter === 'Q2' ? '06' : quarter === 'Q3' ? '09' : '12'}-15`,
    pdfUrl: opts.pdfUrl || null,
    flipbookReady: opts.flipbookReady !== false,
    sections: opts.sections || [],
    workflow: opts.workflow || null,
    featured: !!opts.featured,
    sample: !!opts.sample,
  };
}

export const magazineCatalog = [
  issue(
    'uq-2026-q1',
    'The Dhoni Era',
    'Q1',
    2026,
    'IPL Special',
    'https://images.unsplash.com/photo-1531415074968-076ba3e9f2e4?w=1200&q=80&auto=format&fit=crop',
    {
      featured: true,
      sample: true,
      access: 'free',
      priceINR: 0,
      pageCount: 52,
      sections: [
        {
          id: 'cover-story',
          title: 'Captain Cool — The Final Innings?',
          excerpt: 'As MS Dhoni enters what may be his last IPL chapter, UNTOLD traces the Ranchi boy who became cricket\'s greatest finisher.',
          body: 'From ticket collector at Kharagpur station to lifting the World Cup at Wankhede — Dhoni\'s story is the story of modern Indian cricket. This quarter, we go beyond the helicopter shot.',
          image: 'https://images.unsplash.com/photo-1540747913346-19a32ad3b0f2?w=1000&q=80',
          author: 'UNTOLD Editorial AI',
        },
        {
          id: 'editorial',
          title: 'Letter from the Editor',
          excerpt: 'Welcome to the first UNTOLD E-Magazine of 2026 — where storytelling meets sports intelligence.',
          body: 'This magazine is built by AI agents and approved by humans. Our mission: premium sports journalism at scale. — UNTOLD Editor-in-Chief',
          image: 'https://images.unsplash.com/photo-1504711434969-e33886168f1c?w=1000&q=80',
        },
        {
          id: 'originals',
          title: 'Best of UNTOLD Originals',
          excerpt: 'Rise of Dhoni, India\'s 1983, and Messi vs Ronaldo — our top documentaries this quarter.',
          items: ['UNTOLD: Rise of Dhoni', 'UNTOLD: India\'s 1983', 'UNTOLD: Messi vs Ronaldo'],
        },
        {
          id: 'legends',
          title: 'Sachin Tendulkar — The Billion Dreams',
          excerpt: 'AI-generated deep dive into the God of Cricket\'s legacy metrics.',
          stats: [{ label: 'Test Runs', value: '15,921' }, { label: 'Centuries', value: '100' }],
        },
        {
          id: 'rivalries',
          title: 'India vs Pakistan — Beyond the Border',
          excerpt: 'The rivalry that stops nations. Quarter analysis and historical context.',
        },
        {
          id: 'events',
          title: 'Q1 Event Calendar',
          excerpt: 'IPL 2026, Asia Cup buildup, Wimbledon prep, and F1 season launch.',
        },
        {
          id: 'stats',
          title: 'Cricket Analytics Dashboard',
          excerpt: 'Strike rates, economy trends, and powerplay efficiency — AI charts.',
          chartData: [
            { label: 'Jan', value: 8.2 },
            { label: 'Feb', value: 8.7 },
            { label: 'Mar', value: 9.1 },
          ],
        },
        {
          id: 'trends',
          title: 'Global Sports Intelligence',
          excerpt: 'AI predicts: T20 leagues will dominate viewership growth in 2026.',
        },
      ],
    }
  ),
  issue(
    'uq-2025-q4',
    'Messi vs Ronaldo — Eternal',
    'Q4',
    2025,
    'General Edition',
    'https://images.unsplash.com/photo-1574629810360-7efbbe195018?w=1200&q=80&auto=format&fit=crop',
    {
      access: 'paid',
      priceINR: 149,
      pageCount: 44,
      sections: [
        { id: 'cover-story', title: 'The GOAT Debate Ends?', excerpt: 'Messi\'s Inter Miami triumph reopens football\'s greatest argument.' },
        { id: 'editorial', title: 'Year in Review', excerpt: '2025 — a year of comebacks, controversies, and cinematic sport.' },
        { id: 'legends', title: 'Cristiano Ronaldo at 40', excerpt: 'Still scoring. Still relentless. Still Ronaldo.' },
        { id: 'rivalries', title: 'El Clásico Forever', excerpt: 'Real Madrid vs Barcelona — more than a match.' },
      ],
    }
  ),
  issue(
    'uq-2025-q3',
    'Olympics Aftermath',
    'Q3',
    2025,
    'Olympics Special',
    'https://images.unsplash.com/photo-1461896836934-ffe607ba7a38?w=1200&q=80&auto=format&fit=crop',
    { access: 'premium', priceINR: 99, pageCount: 40 }
  ),
  issue(
    'uq-2025-q2',
    'Champions League Glory',
    'Q2',
    2025,
    'Champions League',
    'https://images.unsplash.com/photo-1522778119026-d647f0596c20?w=1200&q=80&auto=format&fit=crop',
    { access: 'vip', priceINR: 79, pageCount: 38 }
  ),
];

export function getMagazineIssues() {
  return magazineCatalog;
}

export function getFeaturedIssue() {
  return magazineCatalog.find((i) => i.featured) || magazineCatalog[0];
}

export function getIssueById(id) {
  return magazineCatalog.find((i) => i.id === id) || null;
}

export function getFreeSampleIssue() {
  return magazineCatalog.find((i) => i.sample || i.access === 'free') || magazineCatalog[0];
}

export const MOCK_WORKFLOW_JOBS = [
  {
    id: 'job-q2-2026',
    issueId: null,
    theme: 'Champions League',
    quarter: 'Q2',
    year: 2026,
    status: 'writing',
    progress: 42,
    steps: MAGAZINE_WORKFLOW_STEPS.map((s, i) => ({
      ...s,
      status: i === 0 ? 'completed' : i === 1 ? 'processing' : 'pending',
    })),
    createdAt: new Date().toISOString(),
  },
];
