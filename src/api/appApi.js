import { api } from './client';

export const authApi = {
  async login({ email, password }) {
    const tokens = await api.auth.login({ email, password });
    localStorage.setItem('untold-token', tokens.access_token);
    localStorage.setItem('untold-refresh', tokens.refresh_token);
    const user = await api.auth.me();
    return { data: { user, token: tokens.access_token } };
  },

  async register({ name, email, password }) {
    await api.auth.register({ email, password, full_name: name });
    return authApi.login({ email, password });
  },

  async getProfile() {
    const user = await api.auth.me();
    return { data: user };
  },

  async loginGoogle(idToken) {
    const tokens = await api.auth.google(idToken);
    localStorage.setItem('untold-token', tokens.access_token);
    localStorage.setItem('untold-refresh', tokens.refresh_token);
    const user = await api.auth.me();
    return { data: { user, token: tokens.access_token } };
  },
};

export const appApi = {
  async search(query) {
    const { items } = await api.videos.search(query);
    return {
      data: items.map((v) => ({
        id: v.id,
        title: v.title,
        image: v.image_url,
        category: v.category?.name,
        duration: v.duration,
      })),
    };
  },

  async getNotifications() {
    const sub = await api.subscriptions.me();
    const items = [];
    if (sub?.status === 'active') {
      items.push({
        id: 'sub-active',
        title: 'Subscription active',
        body: `Your ${sub.plan} plan is active.`,
        read: false,
        created_at: sub.started_at || new Date().toISOString(),
      });
    }
    return { data: items };
  },

  async submitContact(formData) {
    const res = await api.contact.submit({
      name: formData.name,
      email: formData.email,
      subject: formData.subject,
      message: formData.message,
    });
    return { data: { success: true, message: res.message } };
  },
};

export { api };
