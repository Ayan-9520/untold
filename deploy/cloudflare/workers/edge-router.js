/**
 * UNTOLD Cloudflare Edge Worker
 * - Routes API/gateway traffic to regional origins
 * - Caches safe public GET responses at the edge
 * - Injects tracing and security headers
 */

const CACHEABLE_PREFIXES = [
  '/api/v1/videos',
  '/gateway/v1/videos',
  '/gateway/v2/videos',
  '/gateway/sandbox/v1/videos',
];

const BYPASS_PREFIXES = ['/ready', '/live', '/health', '/metrics', '/ws/'];

function isBypass(pathname) {
  return BYPASS_PREFIXES.some((p) => pathname.startsWith(p));
}

function isCacheableGet(method, pathname) {
  if (method !== 'GET') return false;
  if (isBypass(pathname)) return false;
  return CACHEABLE_PREFIXES.some((p) => pathname === p || pathname.startsWith(p + '/'));
}

function pickRegion(request, env) {
  const forced = request.headers.get('X-UNTOLD-Region');
  if (forced === 'us' || forced === 'eu') return forced;

  const country = request.cf?.country || '';
  const americas = new Set([
    'US', 'CA', 'MX', 'BR', 'AR', 'CL', 'CO', 'PE', 'VE',
  ]);
  if (americas.has(country) && env.API_ORIGIN_US) return 'us';
  return env.DEFAULT_REGION || 'eu';
}

function originForRegion(region, env) {
  if (region === 'us' && env.API_ORIGIN_US) return env.API_ORIGIN_US;
  return env.API_ORIGIN_EU || env.API_ORIGIN_US;
}

function withSecurityHeaders(response, requestId) {
  const headers = new Headers(response.headers);
  headers.set('X-Content-Type-Options', 'nosniff');
  headers.set('X-Frame-Options', 'DENY');
  headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
  if (requestId) headers.set('X-Request-ID', requestId);
  headers.set('X-UNTOLD-Edge', 'cloudflare');
  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers,
  });
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const requestId = request.headers.get('X-Request-ID') || crypto.randomUUID();

    if (isBypass(url.pathname)) {
      const region = pickRegion(request, env);
      const origin = originForRegion(region, env);
      const target = new URL(url.pathname + url.search, origin);
      const res = await fetch(target, request);
      return withSecurityHeaders(res, requestId);
    }

    const isApi =
      url.pathname.startsWith('/api/') ||
      url.pathname.startsWith('/gateway/');

    if (!isApi) {
      return fetch(request);
    }

    const region = pickRegion(request, env);
    const origin = originForRegion(region, env);
    const target = new URL(url.pathname + url.search, origin);

    const forwardHeaders = new Headers(request.headers);
    forwardHeaders.set('X-Request-ID', requestId);
    forwardHeaders.set('X-UNTOLD-Region', region);
    forwardHeaders.set('X-Forwarded-Proto', 'https');
    const clientIp = request.headers.get('CF-Connecting-IP');
    if (clientIp) {
      forwardHeaders.set('X-Forwarded-For', clientIp);
      forwardHeaders.set('X-Real-IP', clientIp);
    }

    const forwardRequest = new Request(target.toString(), {
      method: request.method,
      headers: forwardHeaders,
      body: request.method !== 'GET' && request.method !== 'HEAD' ? request.body : undefined,
      redirect: 'manual',
    });

    if (isCacheableGet(request.method, url.pathname)) {
      const cache = caches.default;
      const cacheKey = new Request(target.toString(), { method: 'GET' });
      let cached = await cache.match(cacheKey);
      if (cached) {
        return withSecurityHeaders(cached, requestId);
      }

      const response = await fetch(forwardRequest);
      if (response.ok) {
        const ttl = parseInt(env.CACHE_TTL_SECONDS || '60', 10);
        const toCache = new Response(response.body, response);
        toCache.headers.set('Cache-Control', `public, max-age=${ttl}, stale-while-revalidate=300`);
        ctx.waitUntil(cache.put(cacheKey, toCache.clone()));
        return withSecurityHeaders(toCache, requestId);
      }
      return withSecurityHeaders(response, requestId);
    }

    const response = await fetch(forwardRequest);
    return withSecurityHeaders(response, requestId);
  },
};
