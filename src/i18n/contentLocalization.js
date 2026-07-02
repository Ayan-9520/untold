import catalogHi from '../locales/catalog/hi.js';
import { isIndianLanguage } from '../data/regionalConfig';

const INDIAN_CATALOG = catalogHi;

function slugify(text = '') {
  return text
    .toLowerCase()
    .replace(/'/g, '')
    .replace(/:/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '');
}

function getCatalog(lang) {
  if (!isIndianLanguage(lang)) return null;
  return INDIAN_CATALOG;
}

export function localizeTitle(title, slug, lang) {
  if (!title || !isIndianLanguage(lang)) return title;
  const catalog = getCatalog(lang);
  if (!catalog) return title;
  const key = slug || slugify(title);
  if (catalog.titles[key]) return catalog.titles[key];
  if (catalog.titlesByEn[title]) return catalog.titlesByEn[title];
  // UNTOLD: prefix pattern
  if (title.startsWith('UNTOLD:')) {
    const rest = title.slice(7).trim();
    const partial = Object.entries(catalog.titlesByEn).find(([en]) => en.endsWith(rest));
    if (partial) return partial[1];
  }
  return title;
}

export function localizeDescription(description, slug, lang) {
  if (!description || !isIndianLanguage(lang)) return description;
  const catalog = getCatalog(lang);
  if (!catalog?.descriptions) return description;
  const key = slug || slugify(description);
  return catalog.descriptions[key] || description;
}

export function localizeCategory(value, lang) {
  if (!value || !isIndianLanguage(lang)) return value;
  const catalog = getCatalog(lang);
  const key = String(value).toLowerCase();
  return catalog?.categories[value] || catalog?.categories[key] || value;
}

export function localizeSport(value, lang) {
  if (!value || !isIndianLanguage(lang)) return value;
  const catalog = getCatalog(lang);
  return catalog?.sports[value] || value;
}

export function localizeFormat(value, lang) {
  if (!value || !isIndianLanguage(lang)) return value;
  const catalog = getCatalog(lang);
  return catalog?.formats[value] || value;
}

export function localizeViews(views, lang, t) {
  if (!views) return views;
  if (!isIndianLanguage(lang)) {
    return typeof views === 'string' && views.includes('views') ? views : `${views} views`;
  }
  const ui = INDIAN_CATALOG.ui;
  if (typeof views === 'string' && views.endsWith('K')) {
    return `${views} ${ui.viewsK}`;
  }
  return `${views} ${ui.views}`;
}

export function localizeVideo(video, lang) {
  if (!video || !isIndianLanguage(lang)) return video;
  const slug = video.slug || slugify(video.title);
  return {
    ...video,
    title: localizeTitle(video.title, slug, lang),
    description: video.description
      ? localizeDescription(video.description, slug, lang)
      : video.description,
    category: localizeCategory(video.category, lang),
    sport: localizeSport(video.sport || video.category, lang),
    format: video.format ? localizeFormat(video.format, lang) : video.format,
    vertical: video.vertical ? localizeCategory(video.vertical, lang) : video.vertical,
    views: video.views ? localizeViews(video.views, lang) : video.views,
  };
}

export function catalogUi(lang, key) {
  if (!isIndianLanguage(lang)) return null;
  return INDIAN_CATALOG.ui[key] || null;
}
