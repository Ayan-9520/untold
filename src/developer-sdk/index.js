/**
 * UNTOLD Developer SDK — REST + GraphQL client for the public API gateway.
 *
 * @example
 * import { UntoldClient } from './developer-sdk';
 * const client = new UntoldClient({ apiKey: 'unt_live_...', environment: 'production' });
 * const videos = await client.videos.list();
 */

const DEFAULT_BASE = typeof import.meta !== 'undefined' && import.meta.env?.VITE_API_URL
  ? import.meta.env.VITE_API_URL.replace(/\/api\/v1\/?$/, '')
  : 'http://localhost:8000';

export class UntoldClient {
  constructor({ apiKey, accessToken, baseUrl = DEFAULT_BASE, environment = 'production', version = 'v1' } = {}) {
    this.apiKey = apiKey;
    this.accessToken = accessToken;
    this.baseUrl = baseUrl.replace(/\/$/, '');
    this.environment = environment;
    this.version = version;
    this._gatewayRoot = environment === 'sandbox' ? '/gateway/sandbox' : '/gateway';
  }

  _headers(extra = {}) {
    const h = {
      Accept: 'application/json',
      'Content-Type': 'application/json',
      'X-API-Version': this.version,
      ...extra,
    };
    if (this.apiKey) h['X-API-Key'] = this.apiKey;
    if (this.accessToken) h.Authorization = `Bearer ${this.accessToken}`;
    return h;
  }

  async _request(method, path, { body, params } = {}) {
    const url = new URL(`${this.baseUrl}${this._gatewayRoot}${path}`);
    if (params) {
      Object.entries(params).forEach(([k, v]) => {
        if (v != null) url.searchParams.set(k, String(v));
      });
    }
    const res = await fetch(url, {
      method,
      headers: this._headers(),
      body: body ? JSON.stringify(body) : undefined,
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      const err = new Error(data.detail || res.statusText);
      err.status = res.status;
      err.data = data;
      throw err;
    }
    return data.data !== undefined && data.meta ? data.data : data;
  }

  get me() {
    return this._request('GET', `/${this.version}/me`);
  }

  get videos() {
    const v = this.version;
    return {
      list: (params) => this._request('GET', `/${v}/videos`, { params }),
      get: (id) => this._request('GET', `/${v}/videos/${id}`),
    };
  }

  get projects() {
    const v = this.version;
    return {
      list: (params) => this._request('GET', `/${v}/projects`, { params }),
      get: (id) => this._request('GET', `/${v}/projects/${id}`),
    };
  }

  get webhooks() {
    return {
      list: () => this._request('GET', '/v1/webhooks'),
      create: (body) => this._request('POST', '/v1/webhooks', { body }),
      delete: (id) => this._request('DELETE', `/v1/webhooks/${id}`),
    };
  }

  async graphql(query, variables = {}) {
    const root = this.environment === 'sandbox' ? '/gateway/sandbox/graphql' : '/gateway/graphql';
    const res = await fetch(`${this.baseUrl}${root}`, {
      method: 'POST',
      headers: this._headers(),
      body: JSON.stringify({ query, variables }),
    });
    const json = await res.json();
    if (json.errors?.length) {
      throw new Error(json.errors[0].message);
    }
    return json.data;
  }
}

/** Portal API — manage keys & usage (requires user JWT). */
export function createDeveloperPortalClient({ baseUrl = `${DEFAULT_BASE}/api/v1`, getToken }) {
  async function req(method, path, body) {
    const token = await getToken();
    const res = await fetch(`${baseUrl}${path}`, {
      method,
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: body ? JSON.stringify(body) : undefined,
    });
    if (res.status === 204) return null;
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || res.statusText);
    return data;
  }

  return {
    register: (data) => req('POST', '/developer/register', data),
    me: () => req('GET', '/developer/me'),
    docs: () => req('GET', '/developer/docs'),
    scopes: () => req('GET', '/developer/scopes'),
    sandbox: () => req('GET', '/developer/sandbox'),
    listKeys: () => req('GET', '/developer/keys'),
    createKey: (data) => req('POST', '/developer/keys', data),
    revokeKey: (id) => req('DELETE', `/developer/keys/${id}`),
    usageOverview: () => req('GET', '/developer/usage/overview'),
    usageTimeseries: (days = 7) => req('GET', `/developer/usage/timeseries?days=${days}`),
    usageEndpoints: () => req('GET', '/developer/usage/endpoints'),
    listWebhooks: () => req('GET', '/developer/webhooks'),
    createWebhook: (data) => req('POST', '/developer/webhooks', data),
    deleteWebhook: (id) => req('DELETE', `/developer/webhooks/${id}`),
    testWebhook: (id) => req('POST', `/developer/webhooks/${id}/test`),
  };
}

export default UntoldClient;
