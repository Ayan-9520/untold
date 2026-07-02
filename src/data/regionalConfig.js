/**
 * Regional configuration — sports priority, featured content, pricing (API-ready)
 */

export const REGIONS = [
  {
    id: 'india',
    label: 'India',
    flag: '🇮🇳',
    currency: 'INR',
    currencySymbol: '₹',
    defaultLanguage: 'hi',
    sports: ['Cricket', 'Kabaddi', 'Football'],
    featuredVideoIds: ['orig-messi-ronaldo', 'leg-jordan', 'orig-senna', 'riv-fed-nadal', 'story-historic', 'leg-ali'],
    featuredEventIds: ['evt-wimbledon', 'evt-ind-eng-test', 'evt-ucl-knockout'],
    paymentMethods: ['UPI', 'Razorpay'],
  },
  {
    id: 'asia',
    label: 'Asia',
    flag: '🌏',
    currency: 'USD',
    currencySymbol: '$',
    defaultLanguage: 'en',
    sports: ['Cricket', 'Football', 'MMA'],
    featuredVideoIds: ['orig-messi-ronaldo', 'leg-sachin', 'short-knockouts', 'riv-messi-ronaldo'],
    featuredEventIds: ['evt-asia-cup', 'evt-ind-pak'],
    paymentMethods: ['Stripe', 'PayPal'],
  },
  {
    id: 'europe',
    label: 'Europe',
    flag: '🇪🇺',
    currency: 'EUR',
    currencySymbol: '€',
    defaultLanguage: 'en',
    sports: ['Football', 'Formula 1', 'Tennis'],
    featuredVideoIds: ['orig-messi-ronaldo', 'leg-messi', 'leg-ronaldo', 'riv-el-clasico', 'riv-fed-nadal', 'orig-senna'],
    featuredEventIds: ['evt-ucl-knockout', 'evt-el-clasico', 'evt-wimbledon'],
    paymentMethods: ['Stripe', 'PayPal'],
  },
  {
    id: 'russia',
    label: 'Russia / CIS',
    flag: '🇷🇺',
    currency: 'RUB',
    currencySymbol: '₽',
    defaultLanguage: 'ru',
    sports: ['Football', 'MMA', 'Hockey'],
    featuredVideoIds: ['short-knockouts', 'leg-tyson', 'riv-messi-ronaldo', 'story-comeback'],
    featuredEventIds: ['evt-ufc-305', 'evt-world-cup-2026'],
    paymentMethods: ['Stripe'],
  },
  {
    id: 'latin-america',
    label: 'Latin America',
    flag: '🌎',
    currency: 'USD',
    currencySymbol: '$',
    defaultLanguage: 'es',
    sports: ['Football', 'Boxing'],
    featuredVideoIds: ['leg-maradona', 'leg-messi', 'leg-pele', 'riv-messi-ronaldo', 'short-goals'],
    featuredEventIds: ['evt-world-cup-2026', 'evt-el-clasico'],
    paymentMethods: ['Stripe', 'PayPal'],
  },
  {
    id: 'middle-east',
    label: 'Middle East',
    flag: '🌍',
    currency: 'AED',
    currencySymbol: 'AED ',
    defaultLanguage: 'ar',
    sports: ['Football', 'Boxing', 'MMA'],
    featuredVideoIds: ['riv-messi-ronaldo', 'short-knockouts', 'leg-ronaldo', 'sec-transfer'],
    featuredEventIds: ['evt-boxing-title', 'evt-ufc-305', 'evt-world-cup-2026'],
    paymentMethods: ['Stripe', 'PayPal'],
  },
  {
    id: 'usa',
    label: 'USA / North America',
    flag: '🇺🇸',
    currency: 'USD',
    currencySymbol: '$',
    defaultLanguage: 'en',
    sports: ['Basketball', 'Football', 'MMA'],
    featuredVideoIds: ['orig-last-dance', 'leg-jordan', 'leg-kobe', 'leg-lebron', 'short-knockouts'],
    featuredEventIds: ['evt-ufc-305', 'evt-pl-final-day'],
    paymentMethods: ['Stripe', 'PayPal'],
  },
];

export const CURRENCIES = [
  { code: 'INR', symbol: '₹', label: 'INR (₹)' },
  { code: 'USD', symbol: '$', label: 'USD ($)' },
  { code: 'EUR', symbol: '€', label: 'EUR (€)' },
  { code: 'GBP', symbol: '£', label: 'GBP (£)' },
  { code: 'RUB', symbol: '₽', label: 'RUB (₽)' },
  { code: 'AED', symbol: 'AED ', label: 'AED' },
];

/** Regional membership pricing per month */
export const MEMBERSHIP_PRICING = {
  INR: { free: 0, premium: 149, vip: 499 },
  USD: { free: 0, premium: 4.99, vip: 12.99 },
  EUR: { free: 0, premium: 4.99, vip: 12.99 },
  GBP: { free: 0, premium: 4.99, vip: 11.99 },
  RUB: { free: 0, premium: 499, vip: 1499 },
  AED: { free: 0, premium: 19, vip: 49 },
};

export const AI_LOCALIZATION_LANGUAGES = [
  { code: 'en', label: 'English', native: 'English' },
  { code: 'hi', label: 'Hindi', native: 'हिन्दी' },
  { code: 'es', label: 'Spanish', native: 'Español' },
  { code: 'ru', label: 'Russian', native: 'Русский' },
  { code: 'ar', label: 'Arabic', native: 'العربية', rtl: true },
];

/** Top Indian languages — shown in quick picker bar */
export const FAMOUS_INDIAN_LANGUAGES = [
  { code: 'hi', label: 'Hindi', native: 'हिन्दी' },
  { code: 'en-IN', label: 'English', native: 'English' },
  { code: 'ta', label: 'Tamil', native: 'தமிழ்' },
  { code: 'te', label: 'Telugu', native: 'తెలుగు' },
  { code: 'bn', label: 'Bengali', native: 'বাংলা' },
  { code: 'mr', label: 'Marathi', native: 'मराठी' },
];

/** Indian languages — full site UI + INR pricing */
export const INDIAN_LANGUAGES = [
  ...FAMOUS_INDIAN_LANGUAGES,
  { code: 'gu', label: 'Gujarati', native: 'ગુજરાતી' },
  { code: 'kn', label: 'Kannada', native: 'ಕನ್ನಡ' },
  { code: 'ml', label: 'Malayalam', native: 'മലയാളം' },
  { code: 'pa', label: 'Punjabi', native: 'ਪੰਜਾਬੀ' },
  { code: 'ur', label: 'Urdu', native: 'اردو', rtl: true },
  { code: 'or', label: 'Odia', native: 'ଓଡ଼ିଆ' },
];

export const INTERNATIONAL_LANGUAGES = [
  { code: 'en', label: 'English', native: 'English' },
  { code: 'ru', label: 'Russian', native: 'Русский' },
  { code: 'es', label: 'Spanish', native: 'Español' },
  { code: 'eu', label: 'Europe', native: 'Europe' },
];

export const LANGUAGES = [...INDIAN_LANGUAGES, ...INTERNATIONAL_LANGUAGES];

const INDIAN_LANG_CODES = new Set(INDIAN_LANGUAGES.map((l) => l.code));

/** Membership currency follows selected language */
export const LANGUAGE_CURRENCY = {
  en: 'USD',
  ru: 'RUB',
  es: 'USD',
  eu: 'EUR',
  hi: 'INR',
  'en-IN': 'INR',
  bn: 'INR',
  ta: 'INR',
  te: 'INR',
  mr: 'INR',
  gu: 'INR',
  kn: 'INR',
  ml: 'INR',
  pa: 'INR',
  ur: 'INR',
  or: 'INR',
};

export const PAYMENTS_BY_LANGUAGE = {
  en: ['Stripe', 'PayPal'],
  ru: ['Stripe'],
  es: ['Stripe', 'PayPal'],
  eu: ['Stripe', 'PayPal'],
  hi: ['UPI', 'Razorpay', 'Stripe'],
  'en-IN': ['UPI', 'Razorpay', 'Stripe'],
  bn: ['UPI', 'Razorpay', 'Stripe'],
  ta: ['UPI', 'Razorpay', 'Stripe'],
  te: ['UPI', 'Razorpay', 'Stripe'],
  mr: ['UPI', 'Razorpay', 'Stripe'],
  gu: ['UPI', 'Razorpay', 'Stripe'],
  kn: ['UPI', 'Razorpay', 'Stripe'],
  ml: ['UPI', 'Razorpay', 'Stripe'],
  pa: ['UPI', 'Razorpay', 'Stripe'],
  ur: ['UPI', 'Razorpay', 'Stripe'],
  or: ['UPI', 'Razorpay', 'Stripe'],
};

export const PHASE1_LANGUAGES = LANGUAGES.map((l) => l.code);

export function isIndianLanguage(lang) {
  return INDIAN_LANG_CODES.has(lang);
}

export function regionForLanguage(lang) {
  return isIndianLanguage(lang) ? 'india' : null;
}

export function currencyForLanguage(lang) {
  return LANGUAGE_CURRENCY[lang] || LANGUAGE_CURRENCY.en;
}

export function paymentsForLanguage(lang) {
  return PAYMENTS_BY_LANGUAGE[lang] || PAYMENTS_BY_LANGUAGE.en;
}

const REGION_KEY = 'untold-region';

export function detectRegion() {
  try {
    const stored = localStorage.getItem(REGION_KEY);
    if (stored) {
      const found = REGIONS.find((r) => r.id === stored);
      if (found) return found.id;
    }
  } catch { /* ignore */ }

  const lang = navigator.language || 'en';
  if (lang === 'hi' || lang === 'en-IN') return 'india';
  if (lang.startsWith('ru')) return 'russia';
  if (lang.startsWith('es')) return 'latin-america';
  if (lang.startsWith('ar')) return 'middle-east';
  if (lang.startsWith('en-GB')) return 'europe';

  const tz = Intl.DateTimeFormat().resolvedOptions().timeZone || '';
  if (tz.includes('Kolkata') || tz.includes('Calcutta')) return 'india';
  if (tz.includes('Europe/Moscow')) return 'russia';
  if (tz.includes('America/')) return 'usa';
  if (tz.includes('Europe/')) return 'europe';
  if (tz.includes('Asia/Dubai')) return 'middle-east';

  return 'usa';
}

export function getRegionById(id) {
  return REGIONS.find((r) => r.id === id) || REGIONS.find((r) => r.id === 'usa');
}

export function persistRegion(id) {
  try { localStorage.setItem(REGION_KEY, id); } catch { /* ignore */ }
}

export function formatPrice(amount, currencyCode) {
  const pricing = MEMBERSHIP_PRICING[currencyCode] || MEMBERSHIP_PRICING.USD;
  const curr = CURRENCIES.find((c) => c.code === currencyCode) || CURRENCIES[1];
  const value = amount ?? 0;
  if (currencyCode === 'INR' || currencyCode === 'RUB') {
    return `${curr.symbol}${Math.round(value)}`;
  }
  if (currencyCode === 'AED') {
    return `${curr.symbol}${Math.round(value)}`;
  }
  return `${curr.symbol}${value.toFixed(2)}`;
}
