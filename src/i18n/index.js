import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import en from '../locales/en.json';
import es from '../locales/es.json';
import ru from '../locales/ru.json';
import eu from '../locales/eu.json';
import hi from '../locales/hi.json';
import { indianLocales } from '../locales/indianLocales';
import { PHASE1_LANGUAGES, isIndianLanguage } from '../data/regionalConfig';

const STORAGE_KEY = 'untold-language';

const RTL_LANGUAGES = new Set(['ur', 'ar']);

function detectLanguage() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored && PHASE1_LANGUAGES.includes(stored)) return stored;
  } catch { /* ignore */ }

  const browser = (navigator.language || 'en').toLowerCase();
  const tz = Intl.DateTimeFormat().resolvedOptions().timeZone || '';
  const inIndia =
    tz.includes('Kolkata') ||
    tz.includes('Calcutta') ||
    browser === 'en-in' ||
    browser.startsWith('hi');

  if (browser.startsWith('hi')) return 'hi';
  if (browser.startsWith('bn')) return 'bn';
  if (browser.startsWith('ta')) return 'ta';
  if (browser.startsWith('te')) return 'te';
  if (browser.startsWith('mr')) return 'mr';
  if (browser.startsWith('gu')) return 'gu';
  if (browser.startsWith('kn')) return 'kn';
  if (browser.startsWith('ml')) return 'ml';
  if (browser.startsWith('pa')) return 'pa';
  if (browser.startsWith('ur')) return 'ur';
  if (browser.startsWith('or')) return 'or';
  if (browser === 'en-in' || (inIndia && browser.startsWith('en'))) return 'en-IN';
  if (inIndia) return 'hi';
  if (browser.startsWith('ru')) return 'ru';
  if (browser.startsWith('es')) return 'es';
  if (
    browser.startsWith('de') ||
    browser.startsWith('fr') ||
    browser.startsWith('it') ||
    browser.startsWith('pt') ||
    browser.startsWith('nl') ||
    browser.startsWith('pl') ||
    browser.startsWith('en-gb') ||
    browser.startsWith('en-ie')
  ) {
    return 'eu';
  }
  return 'en';
}

function applyDocumentLanguage(lng) {
  document.documentElement.lang = lng === 'eu' ? 'en' : lng;
  document.documentElement.dir = RTL_LANGUAGES.has(lng) ? 'rtl' : 'ltr';
}

const resources = {
  en: { translation: en },
  es: { translation: es },
  ru: { translation: ru },
  eu: { translation: eu },
  hi: { translation: hi },
  ...Object.fromEntries(
    Object.entries(indianLocales).map(([code, translation]) => [code, { translation }])
  ),
};

i18n.use(initReactI18next).init({
  resources,
  lng: detectLanguage(),
  fallbackLng: 'en',
  interpolation: { escapeValue: false },
});

i18n.on('languageChanged', (lng) => {
  try {
    localStorage.setItem(STORAGE_KEY, lng);
  } catch { /* ignore */ }
  applyDocumentLanguage(lng);
});

applyDocumentLanguage(i18n.language);

export { isIndianLanguage };
export default i18n;
