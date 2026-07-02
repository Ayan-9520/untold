import { useMemo, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import {
  localizeTitle,
  localizeDescription,
  localizeCategory,
  localizeSport,
  localizeFormat,
  localizeViews,
  localizeVideo,
  catalogUi,
} from '../i18n/contentLocalization';

export function useLocalizedContent() {
  const { i18n, t } = useTranslation();
  const lang = i18n.language;

  const ui = useCallback(
    (key, fallback) => catalogUi(lang, key) || t(`content.ui.${key}`, fallback || key),
    [lang, t]
  );

  const lTitle = useCallback((title, slug) => localizeTitle(title, slug, lang), [lang]);
  const lCategory = useCallback((v) => localizeCategory(v, lang), [lang]);
  const lSport = useCallback((v) => localizeSport(v, lang), [lang]);
  const lFormat = useCallback((v) => localizeFormat(v, lang), [lang]);
  const lViews = useCallback((v) => localizeViews(v, lang, t), [lang, t]);
  const lVideo = useCallback((v) => localizeVideo(v, lang), [lang]);

  return useMemo(
    () => ({
      lang,
      isLocalized: lang === 'hi' || lang.startsWith('en-IN') || ['bn', 'ta', 'te', 'mr', 'gu', 'kn', 'ml', 'pa', 'ur', 'or'].includes(lang),
      localizeTitle: lTitle,
      localizeDescription: (d, slug) => localizeDescription(d, slug, lang),
      localizeCategory: lCategory,
      localizeSport: lSport,
      localizeFormat: lFormat,
      localizeViews: lViews,
      localizeVideo: lVideo,
      ui,
    }),
    [lang, lTitle, lCategory, lSport, lFormat, lViews, lVideo, ui]
  );
}
