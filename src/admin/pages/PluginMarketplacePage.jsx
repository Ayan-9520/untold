import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import StudioPageHeader from '../components/StudioPageHeader';
import { studioPlatform } from '../api/adminApi';
import { studioPath } from '../../config/ecosystem';

const pluginKey = ['plugin-marketplace'];

const CATEGORIES = [
  { id: 'all', label: 'All' },
  { id: 'integration', label: 'Integrations' },
  { id: 'production', label: 'Production' },
  { id: 'developer', label: 'Developer' },
  { id: 'ui', label: 'UI' },
];

function StarRating({ value, count }) {
  const stars = Math.round(value || 0);
  return (
    <span className="text-[10px] dark:text-untold-muted">
      {'★'.repeat(stars)}{'☆'.repeat(5 - stars)}
      {count != null && <span className="ml-1">({count})</span>}
    </span>
  );
}

function PluginCard({ plugin, onInstall, onManage }) {
  const badge = plugin.installed
    ? plugin.enabled
      ? { text: 'Enabled', className: 'text-emerald-400' }
      : { text: 'Disabled', className: 'text-amber-400' }
    : null;

  const hooks = plugin.manifest?.hooks?.length || 0;
  const events = plugin.manifest?.subscribes?.length || 0;

  return (
    <article className="studio-card studio-card--ai flex flex-col h-full">
      <div className="flex items-start justify-between gap-2 mb-3">
        <span className="text-3xl">{plugin.icon}</span>
        <div className="flex flex-col items-end gap-1">
          {badge && <span className={`text-[10px] uppercase tracking-wide ${badge.className}`}>{badge.text}</span>}
          {plugin.update_available && (
            <span className="text-[10px] uppercase tracking-wide text-sky-400">Update available</span>
          )}
        </div>
      </div>
      <h3 className="font-semibold text-sm">{plugin.name}</h3>
      <p className="text-[10px] uppercase tracking-wider mt-1">
        <span className={`studio-category-badge studio-category-badge--${plugin.category || 'production'}`}>
          {plugin.category}
        </span>
      </p>
      <p className="text-[10px] dark:text-untold-muted">by {plugin.author}</p>
      <p className="text-xs dark:text-untold-muted mt-2 flex-1 leading-relaxed">{plugin.description}</p>
      <p className="text-[10px] dark:text-untold-muted mt-2">
        {hooks} hooks · {events} events · {plugin.install_count ?? 0} installs
      </p>
      {(plugin.rating_count > 0 || plugin.average_rating > 0) && (
        <StarRating value={plugin.average_rating} count={plugin.rating_count} />
      )}
      {plugin.current_version && (
        <p className="text-[10px] dark:text-untold-muted">v{plugin.current_version.version}</p>
      )}
      <div className="flex gap-2 mt-4 pt-3 border-t dark:border-white/5">
        {plugin.installed ? (
          <button type="button" className="studio-btn studio-btn--primary text-xs flex-1" onClick={() => onManage(plugin)}>
            Settings
          </button>
        ) : (
          <button type="button" className="studio-btn studio-btn--primary text-xs w-full" onClick={() => onInstall(plugin)}>
            Install
          </button>
        )}
      </div>
    </article>
  );
}

function SettingsField({ fieldKey, schema, value, onChange }) {
  const fieldSchema = schema?.[fieldKey] || {};
  const type = fieldSchema.type || (typeof value === 'boolean' ? 'boolean' : typeof value === 'number' ? 'number' : 'string');

  if (type === 'boolean') {
    return (
      <label className="flex items-center gap-2 text-xs">
        <input type="checkbox" checked={!!value} onChange={(e) => onChange(fieldKey, e.target.checked)} />
        <span>{fieldSchema.title || fieldKey}</span>
      </label>
    );
  }
  return (
    <label className="block text-xs">
      <span className="dark:text-untold-muted">{fieldSchema.title || fieldKey}</span>
      <input
        type={type === 'integer' ? 'number' : 'text'}
        className="studio-input w-full mt-1"
        value={value ?? ''}
        onChange={(e) => onChange(fieldKey, type === 'integer' ? Number(e.target.value) : e.target.value)}
      />
    </label>
  );
}

function ManageDrawer({ installation, plugin, onClose, mutations }) {
  const [settings, setSettings] = useState(installation?.settings || {});
  const [perms, setPerms] = useState(installation?.granted_permissions || []);
  const [tab, setTab] = useState('settings');
  const [rating, setRating] = useState(5);
  const [review, setReview] = useState('');
  const schema = installation?.settings_schema || plugin?.manifest?.settings_schema || {};

  const { data: versions = [] } = useQuery({
    queryKey: [...pluginKey, 'versions', plugin?.slug],
    queryFn: () => studioPlatform.listPluginVersions(plugin.slug),
    enabled: !!plugin?.slug && tab === 'versions',
  });

  const { data: history = [] } = useQuery({
    queryKey: [...pluginKey, 'history', installation?.id],
    queryFn: () => studioPlatform.getPluginInstallationHistory(installation.id),
    enabled: !!installation?.id && tab === 'history',
  });

  const { data: ratings = [] } = useQuery({
    queryKey: [...pluginKey, 'ratings', plugin?.slug],
    queryFn: () => studioPlatform.listPluginRatings(plugin.slug),
    enabled: !!plugin?.slug && tab === 'ratings',
  });

  if (!installation) return null;

  const togglePerm = (p) => {
    setPerms((prev) => (prev.includes(p) ? prev.filter((x) => x !== p) : [...prev, p]));
  };

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      <button type="button" className="absolute inset-0 bg-black/60" onClick={onClose} aria-label="Close" />
      <aside className="relative w-full max-w-md dark:bg-untold-dark border-l dark:border-white/10 p-6 overflow-y-auto">
        <div className="flex items-start justify-between gap-4">
          <div>
            <span className="text-3xl">{plugin.icon}</span>
            <h2 className="text-lg font-semibold mt-2">{plugin.name}</h2>
            <p className="text-xs dark:text-untold-muted mt-1">
              v{installation.installed_version_label || installation.installed_version}
            </p>
          </div>
          <button type="button" className="studio-btn studio-btn--ghost text-xs" onClick={onClose}>
            Close
          </button>
        </div>

        <div className="flex gap-1 mt-4 flex-wrap">
          {['settings', 'permissions', 'versions', 'history', 'ratings'].map((t) => (
            <button
              key={t}
              type="button"
              className={`px-2 py-1 rounded text-[10px] capitalize ${tab === t ? 'bg-untold-gold/20 text-untold-gold' : 'dark:text-untold-muted'}`}
              onClick={() => setTab(t)}
            >
              {t}
            </button>
          ))}
        </div>

        <div className="flex gap-2 mt-4">
          {installation.enabled ? (
            <button type="button" className="studio-btn studio-btn--ghost text-xs" onClick={() => mutations.disable.mutate(installation.id)}>
              Disable
            </button>
          ) : (
            <button type="button" className="studio-btn studio-btn--primary text-xs" onClick={() => mutations.enable.mutate(installation.id)}>
              Enable
            </button>
          )}
          {installation.update_available && (
            <button type="button" className="studio-btn studio-btn--ghost text-xs" onClick={() => mutations.update.mutate(installation.id)}>
              Update
            </button>
          )}
          <button
            type="button"
            className="studio-btn studio-btn--ghost text-xs text-red-400 ml-auto"
            onClick={() => mutations.uninstall.mutate(installation.id)}
          >
            Uninstall
          </button>
        </div>

        {tab === 'settings' && (
        <section className="mt-6">
          <h3 className="text-xs uppercase tracking-wider dark:text-untold-muted mb-3">Settings</h3>
          <div className="space-y-3">
            {Object.keys(settings).map((key) => (
              <SettingsField
                key={key}
                fieldKey={key}
                schema={schema}
                value={settings[key]}
                onChange={(k, v) => setSettings((s) => ({ ...s, [k]: v }))}
              />
            ))}
          </div>
          <button
            type="button"
            className="studio-btn studio-btn--primary text-xs mt-4 w-full"
            onClick={() => mutations.settings.mutate({ id: installation.id, settings })}
          >
            Save settings
          </button>
        </section>
        )}

        {tab === 'permissions' && (
        <section className="mt-6">
          <h3 className="text-xs uppercase tracking-wider dark:text-untold-muted mb-3">Permissions</h3>
          <div className="space-y-2">
            {(installation.available_permissions || []).map((p) => (
              <label key={p} className="flex items-center gap-2 text-xs">
                <input type="checkbox" checked={perms.includes(p)} onChange={() => togglePerm(p)} />
                <code className="text-[10px]">{p}</code>
              </label>
            ))}
          </div>
          <button
            type="button"
            className="studio-btn studio-btn--ghost text-xs mt-3 w-full"
            onClick={() => mutations.permissions.mutate({ id: installation.id, granted_permissions: perms })}
          >
            Update permissions
          </button>
        </section>
        )}

        {tab === 'versions' && (
          <section className="mt-6 space-y-2">
            {versions.map((v) => (
              <div key={v.id} className="text-xs py-2 border-b dark:border-white/5">
                <div className="flex justify-between">
                  <span className="font-mono text-untold-gold">v{v.version_label || v.version}</span>
                  <span className="dark:text-untold-muted">{v.created_at?.slice(0, 10)}</span>
                </div>
                {v.changelog && <p className="dark:text-untold-muted mt-1">{v.changelog}</p>}
              </div>
            ))}
          </section>
        )}

        {tab === 'history' && (
          <section className="mt-6 space-y-2">
            {history.map((h) => (
              <div key={h.id} className="text-xs py-2 border-b dark:border-white/5">
                <span className="uppercase text-untold-gold">{h.action}</span>
                {h.from_version != null && <span className="ml-2 dark:text-untold-muted">v{h.from_version} → v{h.to_version}</span>}
              </div>
            ))}
          </section>
        )}

        {tab === 'ratings' && (
          <section className="mt-6 space-y-4">
            <div className="space-y-2">
              <label className="text-xs dark:text-untold-muted">Your rating</label>
              <select className="studio-input text-xs" value={rating} onChange={(e) => setRating(Number(e.target.value))}>
                {[5, 4, 3, 2, 1].map((n) => <option key={n} value={n}>{n} stars</option>)}
              </select>
              <textarea className="studio-input text-xs min-h-[60px]" placeholder="Review (optional)" value={review} onChange={(e) => setReview(e.target.value)} />
              <button type="button" className="studio-btn studio-btn--primary text-xs w-full" onClick={() => mutations.rate.mutate({ slug: plugin.slug, rating, review })}>
                Submit rating
              </button>
            </div>
            {ratings.map((r) => (
              <div key={r.id} className="text-xs py-2 border-b dark:border-white/5">
                <StarRating value={r.rating} />
                {r.review && <p className="mt-1 dark:text-untold-muted">{r.review}</p>}
              </div>
            ))}
          </section>
        )}

        <section className="mt-6">
          <h3 className="text-xs uppercase tracking-wider dark:text-untold-muted mb-2">Manifest</h3>
          <pre className="text-[10px] dark:bg-black/30 p-3 rounded overflow-x-auto max-h-40">
            {JSON.stringify(plugin.manifest, null, 2)}
          </pre>
        </section>
      </aside>
    </div>
  );
}

export default function PluginMarketplacePage() {
  const [category, setCategory] = useState('all');
  const [search, setSearch] = useState('');
  const [managePlugin, setManagePlugin] = useState(null);
  const queryClient = useQueryClient();

  const { data: overview, isLoading } = useQuery({
    queryKey: [...pluginKey, category, search],
    queryFn: async () => {
      const params = {};
      if (category !== 'all') params.category = category;
      if (search.trim()) params.search = search.trim();
      const [ov, catalog, installed] = await Promise.all([
        studioPlatform.getPluginMarketplaceOverview(),
        studioPlatform.listMarketplacePlugins(params),
        studioPlatform.listInstalledPlugins(),
      ]);
      return { ...ov, plugins: catalog, installations: installed };
    },
  });

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: pluginKey });
    queryClient.invalidateQueries({ queryKey: ['plugin-runtime'] });
  };

  const mutations = {
    install: useMutation({
      mutationFn: (slug) => studioPlatform.installPlugin(slug, {}),
      onSuccess: invalidate,
    }),
    enable: useMutation({
      mutationFn: (id) => studioPlatform.enablePlugin(id),
      onSuccess: invalidate,
    }),
    disable: useMutation({
      mutationFn: (id) => studioPlatform.disablePlugin(id),
      onSuccess: invalidate,
    }),
    settings: useMutation({
      mutationFn: ({ id, settings }) => studioPlatform.updatePluginSettings(id, { settings }),
      onSuccess: invalidate,
    }),
    permissions: useMutation({
      mutationFn: ({ id, granted_permissions }) => studioPlatform.updatePluginPermissions(id, { granted_permissions }),
      onSuccess: invalidate,
    }),
    update: useMutation({
      mutationFn: (id) => studioPlatform.updatePluginVersion(id),
      onSuccess: invalidate,
    }),
    uninstall: useMutation({
      mutationFn: (id) => studioPlatform.uninstallPlugin(id),
      onSuccess: () => {
        setManagePlugin(null);
        invalidate();
      },
    }),
    rate: useMutation({
      mutationFn: ({ slug, rating, review }) => studioPlatform.ratePlugin(slug, { rating, review }),
      onSuccess: invalidate,
    }),
  };

  const plugins = overview?.plugins || [];
  const installation = managePlugin
    ? overview?.installations?.find((i) => i.plugin_slug === managePlugin.slug || i.plugin_id === managePlugin.id)
    : null;

  return (
    <div className="studio-page">
      <StudioPageHeader
        title="Plugin Marketplace"
        description="Install third-party extensions — hooks, events, integrations, and custom Studio UI"
      >
        <Link to={studioPath('plugins/docs')} className="studio-btn studio-btn--ghost text-xs">
          SDK Docs
        </Link>
      </StudioPageHeader>

      {isLoading ? (
        <p className="text-sm dark:text-untold-muted mt-6">Loading plugin marketplace…</p>
      ) : (
        <>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-6">
            <div className="studio-card p-4">
              <div className="text-[10px] uppercase dark:text-untold-muted">Available</div>
              <div className="text-2xl font-semibold">{overview?.total_plugins ?? 0}</div>
            </div>
            <div className="studio-card p-4">
              <div className="text-[10px] uppercase dark:text-untold-muted">Installed</div>
              <div className="text-2xl font-semibold text-untold-gold">{overview?.installed_count ?? 0}</div>
            </div>
            <div className="studio-card p-4">
              <div className="text-[10px] uppercase dark:text-untold-muted">Enabled</div>
              <div className="text-2xl font-semibold text-emerald-400">{overview?.enabled_count ?? 0}</div>
            </div>
            <div className="studio-card p-4">
              <div className="text-[10px] uppercase dark:text-untold-muted">Categories</div>
              <div className="text-2xl font-semibold text-sky-400">{overview?.categories?.length ?? 0}</div>
            </div>
          </div>

          <div className="flex gap-2 mt-6 flex-wrap items-center">
            <input
              className="studio-input text-xs max-w-xs"
              placeholder="Search plugins…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
            {CATEGORIES.map((c) => (
              <button
                key={c.id}
                type="button"
                className={`studio-tab ${category === c.id ? 'studio-tab--active' : ''}`}
                onClick={() => setCategory(c.id)}
              >
                {c.label}
              </button>
            ))}
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 mt-6">
            {plugins.map((plugin) => (
              <PluginCard
                key={plugin.slug}
                plugin={plugin}
                onInstall={(p) => mutations.install.mutate(p.slug)}
                onManage={setManagePlugin}
              />
            ))}
          </div>

          {overview?.recent_events?.length > 0 && (
            <section className="mt-8">
              <h3 className="text-sm font-semibold mb-3">Recent plugin events</h3>
              <div className="studio-card divide-y dark:divide-white/5">
                {overview.recent_events.map((ev) => (
                  <div key={ev.id} className="p-3 flex justify-between text-xs">
                    <span>
                      <code className="text-untold-gold">{ev.plugin_slug}</code> — {ev.event_name}
                    </span>
                    <span className={ev.status === 'success' ? 'text-emerald-400' : 'text-red-400'}>{ev.status}</span>
                  </div>
                ))}
              </div>
            </section>
          )}
        </>
      )}

      {managePlugin && (
        <ManageDrawer
          installation={installation}
          plugin={managePlugin}
          onClose={() => setManagePlugin(null)}
          mutations={mutations}
        />
      )}
    </div>
  );
}
