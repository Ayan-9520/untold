/**
 * UNTOLD 2.0 — revenue model & monetization streams
 */
import { MEMBERSHIP_PRICING, CURRENCIES } from './regionalConfig';

export const REVENUE_STREAMS = [
  {
    id: 'subscriptions',
    label: 'Membership Subscriptions',
    description: 'Free, Premium, and VIP recurring plans',
    icon: '💎',
    primary: true,
  },
  {
    id: 'ads',
    label: 'Advertising',
    description: 'Pre-roll and mid-roll on Free tier',
    icon: '📺',
  },
  {
    id: 'sponsorships',
    label: 'Sponsorships',
    description: 'Branded content rows and event sponsorship',
    icon: '🤝',
  },
  {
    id: 'partnerships',
    label: 'Brand Partnerships',
    description: 'Co-produced originals and exclusive rights',
    icon: '🏆',
  },
  {
    id: 'live_events',
    label: 'Premium Live Events',
    description: 'PPV and VIP-only live sports access',
    icon: '🔴',
  },
  {
    id: 'licensing',
    label: 'Licensing',
    description: 'B2B syndication and regional distribution',
    icon: '🌐',
  },
];

export const MEMBERSHIP_PLANS = [
  {
    id: 'free',
    name: 'Free',
    features: ['Limited catalog access', 'Ads enabled', 'Standard quality'],
    adSupported: true,
  },
  {
    id: 'premium',
    name: 'Premium',
    features: ['Full originals library', 'Ad-free experience', 'HD streaming', 'Offline downloads'],
    adSupported: false,
    popular: true,
  },
  {
    id: 'vip',
    name: 'VIP',
    features: ['Everything in Premium', 'Premium live sports', 'Exclusive content', 'Early access'],
    adSupported: false,
    liveAccess: true,
  },
];

export function getPlanPricing(currency = 'USD') {
  const pricing = MEMBERSHIP_PRICING[currency] || MEMBERSHIP_PRICING.USD;
  const curr = CURRENCIES.find((c) => c.code === currency) || CURRENCIES[1];
  return MEMBERSHIP_PLANS.map((plan) => ({
    ...plan,
    currency,
    currencySymbol: curr.symbol,
    monthlyPrice: pricing[plan.id] ?? 0,
  }));
}
