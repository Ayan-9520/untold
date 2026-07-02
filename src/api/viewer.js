import client from './client';

export const viewerApi = {
  listProfiles: () => client.get('/viewer/profiles').then((r) => r.data),
  createProfile: (data) => client.post('/viewer/profiles', data).then((r) => r.data),
  verifyPin: (profileId, pin) => client.post(`/viewer/profiles/${profileId}/verify-pin`, { pin }).then((r) => r.data),
  deleteProfile: (id) => client.delete(`/viewer/profiles/${id}`),
  getPreferences: () => client.get('/viewer/preferences').then((r) => r.data),
  updatePreferences: (data) => client.patch('/viewer/preferences', data).then((r) => r.data),
  listReminders: () => client.get('/viewer/reminders').then((r) => r.data),
  setReminder: (data) => client.post('/viewer/reminders', data).then((r) => r.data),
  removeReminder: (matchId) => client.delete(`/viewer/reminders/${matchId}`),
};

export default viewerApi;
