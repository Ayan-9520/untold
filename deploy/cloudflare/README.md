# Cloudflare global edge deployment

Deploy the edge router Worker and configure Pages cache headers for UNTOLD.

## Prerequisites

- Cloudflare account with `untold.com` zone
- API token with `Workers Scripts:Edit`, `Zone:Read`
- Regional API load balancer hostnames (from K8s ingress)

## 1. Configure secrets

```bash
cd deploy/cloudflare
cp wrangler.toml.example wrangler.toml   # if using example
npx wrangler secret put API_ORIGIN_EU    # https://eu-lb.untold.com
npx wrangler secret put API_ORIGIN_US    # https://us-lb.untold.com
```

Or set `vars` in `wrangler.toml` for non-secret origins.

## 2. Deploy Worker

```bash
npm install -g wrangler   # or npx wrangler
wrangler deploy
```

Route in Cloudflare dashboard: `api.untold.com/*` → `untold-edge-router`  
Or use `routes` in `wrangler.toml`.

## 3. Pages (SPA)

Connect GitHub repo; build command: `npm run build`; output: `dist`.  
Copy `pages/_headers` to `public/_headers` in the web root (or `dist/_headers` post-build).

## 4. Load Balancer

Create pools `eu-api` and `us-api` with origins pointing to regional ingress IPs/hostnames.  
Health check: HTTPS GET `/ready`, expect 200, interval 30s.

## 5. Cache purge (emergency)

```bash
curl -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/purge_cache" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"purge_everything":true}'
```

See [global-deployment.md](../../docs/global-deployment.md) for full topology.
