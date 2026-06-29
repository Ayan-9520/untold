/**
 * UNTOLD ORIGINALS — subscription plans
 */
import { MEMBERSHIP_PRICING, CURRENCIES } from './regionalConfig';

export const REVENUE_STREAMS = [
  { id: 'subscriptions', label: 'Membership Subscriptions', description: 'Free through Family plans', icon: '💎', primary: true },
  { id: 'ads', label: 'Advertising', description: 'Pre-roll on Free tier', icon: '📺' },
  { id: 'sponsorships', label: 'Sponsorships', description: 'Branded originals & collections', icon: '🤝' },
  { id: 'partnerships', label: 'Brand Partnerships', description: 'Co-produced documentaries', icon: '🏆' },
  { id: 'licensing', label: 'Licensing', description: 'B2B & broadcast syndication', icon: '🌐' },
];

export const MEMBERSHIP_PLANS = [
  {
    id: 'free',
    name: 'Free',
    billing: 'forever',
    features: ['Limited catalog', 'Ads enabled', 'HD streaming', 'Shorts & news'],
    adSupported: true,
  },
  {
    id: 'premium_monthly',
    name: 'Premium Monthly',
    billing: 'month',
    features: ['Full originals library', 'Ad-free', '4K where available', 'Offline downloads', 'Early access'],
    adSupported: false,
    popular: true,
  },
  {
    id: 'premium_yearly',
    name: 'Premium Yearly',
    billing: 'year',
    features: ['Everything in Premium', '2 months free', 'Exclusive documentaries', 'Priority support'],
    adSupported: false,
  },
  {
    id: 'family',
    name: 'Family Plan',
    billing: 'month',
    features: ['Up to 5 profiles', 'Kids mode', '4K on 3 devices', 'All Premium benefits'],
    adSupported: false,
    profiles: 5,
  },
  {
    id: 'student',
    name: 'Student Plan',
    billing: 'month',
    features: ['50% off Premium', 'Valid student ID', 'Full catalog access', 'Ad-free'],
    adSupported: false,
  },
  {
    id: 'vip',
    name: 'VIP',
    billing: 'month',
    features: ['Everything in Premium', 'Live premieres', 'Director cuts', 'Quarterly magazine'],
    adSupported: false,
    liveAccess: true,
  },
];

const PRICE_MAP = {
  free: { USD: 0, INR: 0, EUR: 0 },
  premium_monthly: { USD: 12.99, INR: 499, EUR: 11.99 },
  premium_yearly: { USD: 119, INR: 4499, EUR: 109 },
  family: { USD: 18.99, INR: 699, EUR: 16.99 },
  student: { USD: 6.49, INR: 249, EUR: 5.99 },
  vip: { USD: 24.99, INR: 999, EUR: 22.99 },
};

export function getPlanPricing(currency = 'USD') {
  const curr = CURRENCIES.find((c) => c.code === currency) || CURRENCIES[1];
  return MEMBERSHIP_PLANS.map((plan) => ({
    ...plan,
    currency,
    currencySymbol: curr.symbol,
    monthlyPrice: PRICE_MAP[plan.id]?.[currency] ?? PRICE_MAP[plan.id]?.USD ?? 0,
  }));
}

/** @deprecated use getPlanPricing */
export { MEMBERSHIP_PRICING };
