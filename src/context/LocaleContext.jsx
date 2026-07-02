import { createContext, useContext, useState, useEffect, useCallback, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import {
  REGIONS,
  detectRegion,
  getRegionById,
  persistRegion,
  MEMBERSHIP_PRICING,
  formatPrice,
  currencyForLanguage,
  paymentsForLanguage,
  regionForLanguage,
} from '../data/regionalConfig';
import { api } from '../api/client';
import { mapVideo } from '../api/content';

const LocaleContext = createContext(null);

export function LocaleProvider({ children }) {
  const { i18n } = useTranslation();
  const [regionId, setRegionId] = useState(() => detectRegion());
  const [regionalVideos, setRegionalVideos] = useState([]);

  const region = useMemo(() => getRegionById(regionId), [regionId]);
  const currency = useMemo(() => currencyForLanguage(i18n.language), [i18n.language]);
  const paymentMethods = useMemo(() => paymentsForLanguage(i18n.language), [i18n.language]);

  useEffect(() => {
    persistRegion(regionId);
  }, [regionId]);

  useEffect(() => {
    const indiaRegion = regionForLanguage(i18n.language);
    if (indiaRegion && regionId !== indiaRegion) {
      setRegionId(indiaRegion);
    }
  }, [i18n.language, regionId]);

  useEffect(() => {
    const sports = (region.sports || []).slice(0, 3);
    const fetches = sports.length
      ? sports.map((sport) => api.videos.list({ category: sport.toLowerCase(), page_size: 4 }))
      : [api.videos.list({ trending: true, page_size: 8 })];

    Promise.all(fetches)
      .then((results) => {
        const seen = new Set();
        const items = [];
        results.forEach((r) => {
          r.items.forEach((v) => {
            if (!seen.has(v.id)) {
              seen.add(v.id);
              items.push(mapVideo(v));
            }
          });
        });
        setRegionalVideos(items.slice(0, 8));
      })
      .catch(() => {
        api.videos.list({ trending: true, page_size: 8 })
          .then((r) => setRegionalVideos(r.items.map(mapVideo)))
          .catch(() => setRegionalVideos([]));
      });
  }, [region]);

  const setRegion = useCallback((id) => {
    setRegionId(id);
  }, []);

  const pricing = useMemo(() => MEMBERSHIP_PRICING[currency] || MEMBERSHIP_PRICING.USD, [currency]);

  const value = useMemo(
    () => ({
      region,
      regionId,
      setRegion,
      currency,
      regions: REGIONS,
      regionalVideos,
      pricing,
      formatPrice: (amount) => formatPrice(amount, currency),
      paymentMethods,
    }),
    [region, regionId, setRegion, currency, regionalVideos, pricing, paymentMethods]
  );

  return <LocaleContext.Provider value={value}>{children}</LocaleContext.Provider>;
}

export function useLocale() {
  const ctx = useContext(LocaleContext);
  if (!ctx) throw new Error('useLocale must be used within LocaleProvider');
  return ctx;
}
