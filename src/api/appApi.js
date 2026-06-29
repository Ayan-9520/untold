import { api } from './client';
import { notifications as mockNotifications } from '../data/mockNotifications';

const delay = (ms = 300) => new Promise((r) => setTimeout(r, ms));

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
    await delay(200);
    return { data: mockNotifications };
  },

  async submitContact(formData) {
    await delay(500);
    return { data: { success: true, message: "Thank you for reaching out." } };
  },
};

export { api };
