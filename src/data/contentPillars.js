/**
 * UNTOLD 2.0 — content pillar definitions for admin CMS & platform routing
 */
export const CONTENT_PILLARS = [
  { id: 'originals', label: 'Originals', slug: 'originals', videoType: 'documentary', route: '/originals' },
  { id: 'shorts', label: 'Shorts', slug: 'shorts', videoType: 'short', route: '/shorts' },
  { id: 'legends', label: 'Legends', slug: 'legends', videoType: 'documentary', route: '/legends' },
  { id: 'rivalries', label: 'Rivalries', slug: 'rivalries', videoType: 'documentary', route: '/rivalries' },
  { id: 'stories', label: 'Stories', slug: 'stories', videoType: 'documentary', route: '/stories' },
  { id: 'secrets', label: 'Secrets', slug: 'secrets', videoType: 'documentary', route: '/secrets' },
  { id: 'events', label: 'Events', slug: 'events', catalog: 'events', route: '/events' },
  { id: 'live', label: 'Live', slug: 'live', catalog: 'events', route: '/live' },
  { id: 'news', label: 'News', slug: 'news', catalog: 'news', route: '/news' },
];

export const AI_LOCALIZATION_LANGUAGES = [
  { code: 'en', label: 'English', flag: '🇬🇧' },
  { code: 'hi', label: 'Hindi', flag: '🇮🇳' },
  { code: 'es', label: 'Spanish', flag: '🇪🇸' },
  { code: 'ru', label: 'Russian', flag: '🇷🇺' },
  { code: 'ar', label: 'Arabic', flag: '🇸🇦', rtl: true },
];

export const AI_PIPELINE_STEPS = [
  { id: 'speech_to_text', label: 'Speech-to-Text' },
  { id: 'script_cleanup', label: 'Script Cleanup' },
  { id: 'translation', label: 'Translation' },
  { id: 'subtitles', label: 'Subtitle Generation' },
  { id: 'dubbing', label: 'AI Dubbing' },
  { id: 'metadata', label: 'Metadata Localization' },
];
