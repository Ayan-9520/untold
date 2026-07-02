import client from './client';

export const platformApi = {
  async getPage(slug) {
    const { data } = await client.get(`/platform/pages/${slug}`);
    return data;
  },
  async listFaq() {
    const { data } = await client.get('/platform/faq');
    return data;
  },
  async validatePromo(code, planSlug) {
    const { data } = await client.post('/platform/promo/validate', { code, plan_slug: planSlug });
    return data;
  },
};

export default platformApi;
