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
} from '../data/regionalConfig';
import { videoCatalog } from '../data/videoCatalog';

const LocaleContext = createContext(null);

export function LocaleProvider({ children }) {
  const { i18n } = useTranslation();
  const [regionId, setRegionId] = useState(() => detectRegion());

  const region = useMemo(() => getRegionById(regionId), [regionId]);
  const currency = useMemo(() => currencyForLanguage(i18n.language), [i18n.language]);
  const paymentMethods = useMemo(() => paymentsForLanguage(i18n.language), [i18n.language]);

  useEffect(() => {
    persistRegion(regionId);
  }, [regionId]);

  const setRegion = useCallback((id) => {
    setRegionId(id);
  }, []);

  const regionalVideos = useMemo(() => {
    const ids = region.featuredVideoIds || [];
    const featured = ids.map((id) => videoCatalog.find((v) => v.id === id)).filter(Boolean);
    const sports = new Set(region.sports || []);
    const sportBased = videoCatalog.filter((v) => sports.has(v.sport) && !ids.includes(v.id));
    return [...featured, ...sportBased].slice(0, 8);
  }, [region]);

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
