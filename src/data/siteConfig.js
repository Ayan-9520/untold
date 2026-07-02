/**
 * Explore page configuration — sports, categories, sorting
 */

export const EXPLORE_SPORTS = [
  'All',
  'Cricket',
  'Football',
  'Tennis',
  'Formula 1',
  'Boxing',
  'MMA',
  'Olympics',
  'Kabaddi',
  'Wrestling',
];

export const EXPLORE_CATEGORIES = [
  { slug: 'originals', name: 'Originals', path: '/originals', description: 'Flagship documentaries & films' },
  { slug: 'shorts', name: 'Shorts', path: '/shorts', description: 'Bite-sized moments' },
  { slug: 'legends', name: 'Legends', path: '/legends', description: 'Athlete legacy stories' },
  { slug: 'rivalries', name: 'Rivalries', path: '/rivalries', description: 'Greatest feuds' },
  { slug: 'stories', name: 'Stories', path: '/stories', description: 'Inspirational narratives' },
  { slug: 'secrets', name: 'Secrets', path: '/secrets', description: 'Untold truths' },
  { slug: 'events', name: 'Events', path: '/events', description: 'Tournaments & coverage' },
  { slug: 'live', name: 'Live', path: '/live', description: 'Live sports now' },
  { slug: 'news', name: 'News', path: '/news', description: 'Latest sports news' },
];

export const SORT_OPTIONS = [
  { value: 'popular', label: 'Popularity' },
  { value: 'latest', label: 'Latest Releases' },
  { value: 'title', label: 'A – Z' },
];

export const FOOTER_CONTACT = {
  company: 'UNTOLD Media Pvt. Ltd.',
  address: 'Lotus Corporate Park, Tower B, 5th Floor, Goregaon East, Mumbai, Maharashtra 400063, India',
  email: 'support@untold.com',
  phone: '+91 98765 43210',
  mapQuery: 'Lotus Corporate Park Goregaon East Mumbai',
  mapLat: 19.1631,
  mapLng: 72.8614,
  grievanceOfficer: 'Rajesh Mehta',
  grievanceEmail: 'grievance@untold.com',
  grievancePhone: '+91 98765 43211',
};

export const SOCIAL_LINKS = [
  { label: 'YouTube', href: 'https://youtube.com', icon: 'youtube' },
  { label: 'Instagram', href: 'https://instagram.com', icon: 'instagram' },
  { label: 'X', href: 'https://x.com', icon: 'x' },
  { label: 'LinkedIn', href: 'https://linkedin.com', icon: 'linkedin' },
  { label: 'Facebook', href: 'https://facebook.com', icon: 'facebook' },
];
