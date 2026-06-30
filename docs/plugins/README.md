# UNTOLD Plugin SDK

Production-grade extensibility platform for third-party Studio developers.

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────────┐
│  Plugin Catalog │────▶│  Installations   │────▶│  Event Bus / Hooks  │
│  (marketplace)  │     │  settings/perms  │     │  workflow, collab…  │
└─────────────────┘     └──────────────────┘     └─────────────────────┘
         │                        │                         │
         ▼                        ▼                         ▼
  Backend SDK              Frontend SDK              plugin_event_log
  BasePlugin               createPlugin()              audit trail
```

## Packages

| Layer | Path | Purpose |
|-------|------|---------|
| Backend SDK | `backend/app/plugins/sdk/` | `BasePlugin`, `PluginContext` |
| Domain | `backend/app/domain/plugins/` | Events, hooks, registry, samples |
| Frontend SDK | `src/plugin-sdk/` | `createPlugin`, `runHooks`, `PluginProvider` |
| API | `/studio/platform/plugins/*` | Marketplace, settings, runtime |
| UI | `/studio/plugins` | Marketplace + settings drawer |
| Docs | `/studio/plugins/docs` | In-app SDK reference |

## Quick start

### 1. Frontend plugin

```javascript
import { createPlugin, HOOKS, EVENTS } from '@/plugin-sdk';

createPlugin({
  manifest: {
    slug: 'my-branding',
    name: 'My Branding',
    hooks: [HOOKS.SEO_FORMAT_TITLE],
    subscribes: [EVENTS.WORKFLOW_RUN_FINISHED],
    permissions: ['project.read'],
  },
  setup(api) {
    api.onHook(HOOKS.SEO_FORMAT_TITLE, (p) => ({
      title: `${p.title} | My Brand`,
    }));
  },
});
```

Register the module in your build, then publish via `POST /studio/platform/plugins/register`.

### 2. Backend plugin

```python
from app.plugins.sdk import BasePlugin, PluginContext

class MyPlugin(BasePlugin):
    slug = "my-branding"

    def on_hook(self, ctx: PluginContext, hook_name: str, payload: dict):
        if hook_name == "seo.format_title":
            return {"title": f"{payload['title']} | My Brand"}
```

Register in `BACKEND_PLUGIN_REGISTRY` or submit manifest with `entry_points.backend`.

### 3. Install & configure

1. Open **Studio → Plugin Marketplace**
2. Install your plugin
3. Grant permissions (scoped capabilities)
4. Configure settings (webhook URLs, formatting rules, etc.)
5. Enable — runtime loads via `GET /studio/platform/plugins/runtime`

## Events

Plugins subscribe to studio events via `manifest.subscribes`:

- `workflow.run.finished` — workflow completed
- `workflow.node.completed` — single node done
- `collab.comment.created` — new collaboration comment
- `publish.completed` — content published
- `plugin.installed` — plugin lifecycle

## Hooks

Plugins register handlers via `manifest.hooks`:

- `seo.format_title` / `seo.format_description`
- `workflow.before_node` / `workflow.after_node`
- `dashboard.widgets` — inject dashboard widgets (frontend)
- `nav.items` — sidebar items (frontend)

## Permissions

Scoped capabilities enforced at runtime:

- `webhook.send`, `notification.send`
- `workflow.read`, `workflow.write`
- `project.read`, `project.write`
- `collab.read`, `collab.write`
- `admin.read`, `storage.read`, `publish.schedule`, `ai.generate`

Users grant permissions per installation in the marketplace settings drawer.

## Sample plugins

| Slug | Type | Description |
|------|------|-------------|
| `slack-notify` | Event | Slack webhook alerts |
| `custom-seo-formatter` | Hook | SEO title/description rules |
| `workflow-logger` | Event + Hook | Node execution audit |
| `dashboard-widgets` | Hook | Custom dashboard widgets |

## Database

Migration: `035_plugin_sdk`

```bash
cd backend && python -m alembic upgrade head
```

## API reference

See in-app docs at `/studio/plugins/docs` or `GET /studio/platform/plugins/docs`.
