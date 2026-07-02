import client from './client';

export const membershipApi = {
  async getPlans(currency = 'USD', region = 'usa') {
    const { data } = await client.get('/plans', { params: { currency, region } });
    return data;
  },

  async getSubscription() {
    const { data } = await client.get('/membership/me');
    return data;
  },

  async cancelSubscription() {
    const { data } = await client.post('/membership/cancel');
    return data;
  },

  async getPaymentHistory() {
    const { data } = await client.get('/membership/payments');
    return data;
  },

  async subscribe({ planSlug, currency, region, provider }) {
    const { data } = await client.post('/subscribe', {
      plan_slug: planSlug,
      currency,
      region,
      provider,
    });
    return data;
  },

  async createOrder({ planSlug, currency, region, provider, promoCode, billingCycle }) {
    const { data } = await client.post('/payments/create-order', {
      plan_slug: planSlug,
      currency,
      region,
      provider,
      promo_code: promoCode || undefined,
      billing_cycle: billingCycle || 'monthly',
    });
    return data;
  },

  async verifyPayment({ provider, paymentId, orderId, paymentExternalId, signature }) {
    const { data } = await client.post('/payments/verify', {
      provider,
      payment_id: paymentId,
      order_id: orderId,
      payment_external_id: paymentExternalId,
      signature,
    });
    return data;
  },
};

export default membershipApi;
