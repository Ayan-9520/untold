import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import en from '../locales/en.json';
import es from '../locales/es.json';
import ru from '../locales/ru.json';
import eu from '../locales/eu.json';
import { PHASE1_LANGUAGES } from '../data/regionalConfig';

const STORAGE_KEY = 'untold-language';

function detectLanguage() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored && PHASE1_LANGUAGES.includes(stored)) return stored;
    if (stored === 'hi' || stored === 'ar') return 'en';
  } catch { /* ignore */ }

  const browser = (navigator.language || 'en').toLowerCase();
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

i18n.use(initReactI18next).init({
  resources: {
    en: { translation: en },
    es: { translation: es },
    ru: { translation: ru },
    eu: { translation: eu },
  },
  lng: detectLanguage(),
  fallbackLng: 'en',
  interpolation: { escapeValue: false },
});

i18n.on('languageChanged', (lng) => {
  try {
    localStorage.setItem(STORAGE_KEY, lng);
  } catch { /* ignore */ }
  document.documentElement.lang = lng === 'eu' ? 'en' : lng;
  document.documentElement.dir = 'ltr';
});

document.documentElement.lang = i18n.language === 'eu' ? 'en' : i18n.language;
document.documentElement.dir = 'ltr';

export default i18n;
