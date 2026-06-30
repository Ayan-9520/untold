import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import StudioPageHeader from '../components/StudioPageHeader';
import { studioPlatform } from '../api/adminApi';
import { studioPath } from '../../config/ecosystem';

export default function PluginDocsPage() {
  const { data: docs, isLoading } = useQuery({
    queryKey: ['plugin-sdk-docs'],
    queryFn: () => studioPlatform.getPluginSdkDocs(),
  });

  return (
    <div className="studio-page max-w-4xl">
      <StudioPageHeader
        title="Plugin SDK Documentation"
        description="Build third-party extensions for UNTOLD Studio — frontend SDK, backend SDK, events, hooks, and permissions"
      >
        <Link to={studioPath('plugins')} className="studio-btn studio-btn--ghost text-xs">
          Marketplace
        </Link>
      </StudioPageHeader>

      {isLoading ? (
        <p className="text-sm dark:text-untold-muted mt-6">Loading documentation…</p>
      ) : (
        <div className="mt-8 space-y-10">
          <section>
            <h2 className="text-lg font-semibold mb-3">Quick start</h2>
            <div className="studio-card p-4 space-y-4 text-sm dark:text-untold-muted">
              <p>
                Plugins extend UNTOLD Studio via <strong className="text-white">hooks</strong> (transform data at extension
                points), <strong className="text-white">events</strong> (react to studio activity), and optional{' '}
                <strong className="text-white">settings UI</strong>.
              </p>
              <div>
                <h3 className="text-xs uppercase tracking-wider text-untold-gold mb-2">Frontend (JavaScript)</h3>
                <pre className="text-xs dark:bg-black/40 p-4 rounded overflow-x-auto">{`import { createPlugin, HOOKS, EVENTS } from '@/plugin-sdk';

createPlugin({
  manifest: { slug: 'my-plugin', name: 'My Plugin', hooks: [HOOKS.SEO_FORMAT_TITLE] },
  setup(api) {
    api.onHook(HOOKS.SEO_FORMAT_TITLE, (payload) => ({
      title: \`\${payload.title} | My Brand\`,
    }));
    api.onEvent(EVENTS.WORKFLOW_RUN_FINISHED, (payload) => {
      console.log('Workflow done', payload.run_id);
    });
  },
});`}</pre>
              </div>
              <div>
                <h3 className="text-xs uppercase tracking-wider text-untold-gold mb-2">Backend (Python)</h3>
                <pre className="text-xs dark:bg-black/40 p-4 rounded overflow-x-auto">{`from app.plugins.sdk import BasePlugin, PluginContext

class MyPlugin(BasePlugin):
    slug = "my-plugin"

    def on_event(self, ctx: PluginContext, event_name, payload):
        if event_name == "workflow.run.finished":
            return {"notified": True}

    def on_hook(self, ctx, hook_name, payload):
        if hook_name == "seo.format_title":
            return {"title": f"{payload['title']} | UNTOLD"}`}</pre>
              </div>
            </div>
          </section>

          <section>
            <h2 className="text-lg font-semibold mb-3">Manifest schema</h2>
            <pre className="text-xs studio-card p-4 overflow-x-auto max-h-96">
              {JSON.stringify(docs?.manifest_example, null, 2)}
            </pre>
          </section>

          <section>
            <h2 className="text-lg font-semibold mb-3">Events ({Object.keys(docs?.events || {}).length})</h2>
            <div className="studio-card divide-y dark:divide-white/5">
              {Object.entries(docs?.events || {}).map(([name, meta]) => (
                <div key={name} className="p-4">
                  <code className="text-untold-gold text-sm">{name}</code>
                  <p className="text-xs dark:text-untold-muted mt-1">{meta.label}</p>
                  <p className="text-[10px] uppercase mt-1 dark:text-untold-muted">{meta.category}</p>
                </div>
              ))}
            </div>
          </section>

          <section>
            <h2 className="text-lg font-semibold mb-3">Hooks ({Object.keys(docs?.hooks || {}).length})</h2>
            <div className="studio-card divide-y dark:divide-white/5">
              {Object.entries(docs?.hooks || {}).map(([name, meta]) => (
                <div key={name} className="p-4">
                  <code className="text-untold-gold text-sm">{name}</code>
                  <p className="text-xs dark:text-untold-muted mt-1">{meta.description}</p>
                </div>
              ))}
            </div>
          </section>

          <section>
            <h2 className="text-lg font-semibold mb-3">Permissions</h2>
            <div className="grid sm:grid-cols-2 gap-3">
              {Object.entries(docs?.permissions || {}).map(([key, meta]) => (
                <div key={key} className="studio-card p-4">
                  <code className="text-xs text-untold-gold">{key}</code>
                  <p className="text-sm font-medium mt-1">{meta.label}</p>
                  <p className="text-xs dark:text-untold-muted mt-1">{meta.description}</p>
                  <span
                    className={`text-[10px] uppercase mt-2 inline-block ${
                      meta.risk === 'high' ? 'text-red-400' : meta.risk === 'medium' ? 'text-amber-400' : 'text-emerald-400'
                    }`}
                  >
                    {meta.risk} risk
                  </span>
                </div>
              ))}
            </div>
          </section>

          <section>
            <h2 className="text-lg font-semibold mb-3">API endpoints</h2>
            <div className="studio-card p-4 text-xs font-mono space-y-1 dark:text-untold-muted">
              <p>GET /studio/platform/plugins/catalog</p>
              <p>POST /studio/platform/plugins/catalog/:slug/install</p>
              <p>PATCH /studio/platform/plugins/installations/:id/settings</p>
              <p>GET /studio/platform/plugins/runtime</p>
              <p>GET /studio/platform/plugins/docs</p>
              <p>POST /studio/platform/plugins/register</p>
            </div>
          </section>

          <section>
            <h2 className="text-lg font-semibold mb-3">Sample plugins</h2>
            <ul className="list-disc list-inside text-sm dark:text-untold-muted space-y-1">
              <li>
                <strong className="text-white">slack-notify</strong> — webhook alerts for workflows and publishing
              </li>
              <li>
                <strong className="text-white">custom-seo-formatter</strong> — SEO title/description hooks
              </li>
              <li>
                <strong className="text-white">workflow-logger</strong> — audit logging for node execution
              </li>
              <li>
                <strong className="text-white">dashboard-widgets</strong> — custom dashboard widgets via hooks
              </li>
            </ul>
            <p className="text-xs dark:text-untold-muted mt-3">
              Source: <code>src/plugin-sdk/samples/</code> and <code>backend/app/domain/plugins/samples/</code>
            </p>
          </section>
        </div>
      )}
    </div>
  );
}
