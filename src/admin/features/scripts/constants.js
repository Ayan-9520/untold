export const SCRIPT_AI_GROUPS = [
  {
    id: 'core',
    label: 'Core',
    actions: [
      { id: 'generate', label: 'Generate', icon: '✨' },
      { id: 'rewrite', label: 'Rewrite', icon: '✏️' },
      { id: 'expand', label: 'Expand', icon: '📖' },
      { id: 'shorten', label: 'Shorten', icon: '✂️' },
      { id: 'grammar', label: 'Grammar', icon: '📝' },
      { id: 'tone', label: 'Tone', icon: '🎭' },
    ],
  },
  {
    id: 'styles',
    label: 'Broadcast styles',
    actions: [
      { id: 'style_netflix', label: 'Netflix', icon: '🎬' },
      { id: 'style_bbc', label: 'BBC', icon: '📺' },
      { id: 'style_espn', label: 'ESPN', icon: '🏆' },
      { id: 'style_documentary', label: 'Documentary', icon: '🎥' },
      { id: 'style_interview', label: 'Interview', icon: '🎤' },
      { id: 'style_podcast', label: 'Podcast', icon: '🎧' },
    ],
  },
  {
    id: 'structure',
    label: 'Structure',
    actions: [
      { id: 'chapter', label: 'Chapter', icon: '📑' },
      { id: 'scene', label: 'Scene', icon: '🎞️' },
      { id: 'hook', label: 'Hook', icon: '🪝' },
      { id: 'cta', label: 'CTA', icon: '📣' },
    ],
  },
  {
    id: 'language',
    label: 'Language',
    actions: [{ id: 'translate', label: 'Translate', icon: '🌐' }],
  },
];

export const ALL_SCRIPT_ACTIONS = SCRIPT_AI_GROUPS.flatMap((g) => g.actions);

export const SCRIPT_LANGUAGES = [
  { code: 'es', label: 'Spanish' },
  { code: 'fr', label: 'French' },
  { code: 'de', label: 'German' },
  { code: 'pt', label: 'Portuguese' },
  { code: 'hi', label: 'Hindi' },
  { code: 'ar', label: 'Arabic' },
  { code: 'ja', label: 'Japanese' },
  { code: 'zh', label: 'Chinese' },
];

export const SCRIPT_TONES = [
  'authoritative',
  'conversational',
  'dramatic',
  'inspirational',
  'investigative',
  'intimate',
];
