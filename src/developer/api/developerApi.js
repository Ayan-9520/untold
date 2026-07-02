import { apiUrl, getApiBase } from '../../config/runtime';

const API_BASE = getApiBase();

async function devRequest(method, path, body) {
  const token = localStorage.getItem('untold-token');
  const res = await fetch(apiUrl(path), {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (res.status === 204) return null;
  const data = await res.json();
  if (!res.ok) throw Object.assign(new Error(data.detail || res.statusText), { status: res.status, data });
  return data;
}

export const developerApi = {
  register: (data) => devRequest('POST', '/developer/register', data),
  me: () => devRequest('GET', '/developer/me'),
  docs: () => devRequest('GET', '/developer/docs'),
  scopes: () => devRequest('GET', '/developer/scopes'),
  sandbox: () => devRequest('GET', '/developer/sandbox'),
  listKeys: () => devRequest('GET', '/developer/keys'),
  createKey: (data) => devRequest('POST', '/developer/keys', data),
  revokeKey: (id) => devRequest('DELETE', `/developer/keys/${id}`),
  usageOverview: () => devRequest('GET', '/developer/usage/overview'),
  usageTimeseries: (days = 7) => devRequest('GET', `/developer/usage/timeseries?days=${days}`),
  usageEndpoints: () => devRequest('GET', '/developer/usage/endpoints'),
  listWebhooks: () => devRequest('GET', '/developer/webhooks'),
  createWebhook: (data) => devRequest('POST', '/developer/webhooks', data),
  deleteWebhook: (id) => devRequest('DELETE', `/developer/webhooks/${id}`),
  testWebhook: (id) => devRequest('POST', `/developer/webhooks/${id}/test`),
  webhookDeliveries: (id, limit = 20) => devRequest('GET', `/developer/webhooks/${id}/deliveries?limit=${limit}`),
};
