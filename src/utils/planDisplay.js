import { MEMBERSHIP_PRICING, formatPrice } from '../data/regionalConfig';

const PLAN_META = {
  free: {
    highlight: false,
    periodKey: 'forever',
    ctaKey: 'currentPlan',
  },
  premium: {
    highlight: true,
    periodKey: 'perMonth',
    ctaKey: 'startTrial',
  },
  vip: {
    highlight: false,
    periodKey: 'perMonth',
    ctaKey: 'getVip',
  },
};

const FEATURE_KEYS = {
  free: 'membership.freeFeatures',
  premium: 'membership.premiumFeatures',
  vip: 'membership.vipFeatures',
};

export function buildFallbackPlans(currency, t) {
  const pricing = MEMBERSHIP_PRICING[currency] || MEMBERSHIP_PRICING.USD;
  return ['free', 'premium', 'vip'].map((slug) => {
    const meta = PLAN_META[slug];
    const monthly = pricing[slug];
    return {
      id: slug,
      slug,
      name: t(`membership.${slug}`),
      priceMonthly: monthly,
      priceAnnual: slug === 'free' ? 0 : Math.round(monthly * 10 * 100) / 100,
      period: t(`membership.${meta.periodKey}`),
      features: t(FEATURE_KEYS[slug], { returnObjects: true }),
      cta: t(`membership.${meta.ctaKey}`),
      highlight: meta.highlight,
    };
  });
}

export function mapApiPlans(plans, currency, t) {
  return plans.map((p) => ({
    id: p.slug,
    slug: p.slug,
    name: p.name,
    priceMonthly: p.price,
    priceAnnual: p.slug === 'free' ? 0 : Math.round(p.price * 10 * 100) / 100,
    period: p.slug === 'free' ? t('membership.forever') : t('membership.perMonth'),
    features: p.features,
    cta: p.slug === 'free' ? t('membership.currentPlan') : t(`membership.${p.slug === 'vip' ? 'getVip' : 'startTrial'}`),
    highlight: p.highlight || p.slug === 'premium',
  }));
}

export function displayPrice(plan, currency, billingCycle) {
  const amount = billingCycle === 'annual' ? plan.priceAnnual : plan.priceMonthly;
  return formatPrice(amount, currency);
}
