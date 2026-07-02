import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import StudioPageHeader from '../components/StudioPageHeader';
import {
  AgentAnalyticsPanel,
  AgentLogsPanel,
  AgentMemoryPanel,
  AgentMonitoringPanel,
  AgentSchedulesPanel,
} from '../components/AgentPlatformPanels';
import { studioPlatform } from '../api/adminApi';
import { studioPath } from '../../config/ecosystem';

const marketplaceKey = ['agent-marketplace'];

const CATEGORIES = [
  { id: 'all', label: 'All' },
  { id: 'intelligence', label: 'Intelligence' },
  { id: 'production', label: 'Production' },
  { id: 'creative', label: 'Creative' },
  { id: 'distribution', label: 'Distribution' },
  { id: 'business', label: 'Business' },
];

function AgentCard({ agent, onInstall, onManage }) {
  const badge = agent.installed
    ? agent.enabled
      ? { text: 'Enabled', className: 'text-emerald-400' }
      : { text: 'Disabled', className: 'text-amber-400' }
    : null;

  return (
    <article className="studio-card studio-card--ai flex flex-col h-full">
      <div className="flex items-start justify-between gap-2 mb-3">
        <span className="text-3xl">{agent.icon}</span>
        <div className="flex flex-col items-end gap-1">
          {badge && <span className={`text-[10px] uppercase tracking-wide ${badge.className}`}>{badge.text}</span>}
          {agent.update_available && (
            <span className="text-[10px] uppercase tracking-wide text-sky-400">Update available</span>
          )}
        </div>
      </div>
      <h3 className="font-semibold text-sm">{agent.name}</h3>
      <p className="text-[10px] uppercase tracking-wider mt-1">
        <span className={`studio-category-badge studio-category-badge--${agent.category || 'production'}`}>
          {agent.category}
        </span>
      </p>
      <p className="text-xs dark:text-untold-muted mt-2 flex-1 leading-relaxed">{agent.description}</p>
      {agent.current_version && (
        <p className="text-[10px] dark:text-untold-muted mt-2">v{agent.current_version.version}</p>
      )}
      <div className="flex gap-2 mt-4 pt-3 border-t dark:border-white/5">
        {agent.installed ? (
          <>
            <button type="button" className="studio-btn studio-btn--primary text-xs flex-1" onClick={() => onManage(agent)}>
              Manage
            </button>
            {agent.studio_route && (
              <Link to={studioPath(agent.studio_route)} className="studio-btn studio-btn--ghost text-xs">
                Open
              </Link>
            )}
          </>
        ) : (
          <button type="button" className="studio-btn studio-btn--primary text-xs w-full" onClick={() => onInstall(agent)}>
            Install
          </button>
        )}
      </div>
    </article>
  );
}

function ConfigField({ fieldKey, value, onChange }) {
  const type = typeof value === 'boolean' ? 'checkbox' : typeof value === 'number' ? 'number' : 'text';
  if (Array.isArray(value)) {
    return (
      <label className="block text-xs">
        <span className="dark:text-untold-muted">{fieldKey}</span>
        <input
          className="studio-input w-full mt-1"
          value={value.join(', ')}
          onChange={(e) => onChange(fieldKey, e.target.value.split(',').map((s) => s.trim()).filter(Boolean))}
        />
      </label>
    );
  }
  if (type === 'checkbox') {
    return (
      <label className="flex items-center gap-2 text-xs">
        <input type="checkbox" checked={!!value} onChange={(e) => onChange(fieldKey, e.target.checked)} />
        <span>{fieldKey}</span>
      </label>
    );
  }
  return (
    <label className="block text-xs">
      <span className="dark:text-untold-muted">{fieldKey}</span>
      <input
        type={type}
        className="studio-input w-full mt-1"
        value={value ?? ''}
        onChange={(e) => onChange(fieldKey, type === 'number' ? Number(e.target.value) : e.target.value)}
      />
    </label>
  );
}

function ManageDrawer({ installation, agent, onClose, mutations }) {
  const [config, setConfig] = useState(installation?.config || {});
  const [permissions, setPermissions] = useState(installation?.granted_permissions || []);
  const [tab, setTab] = useState('config');

  const { data: history } = useQuery({
    queryKey: [...marketplaceKey, 'history', installation?.id],
    queryFn: () => studioPlatform.getAgentInstallationHistory(installation.id),
    enabled: !!installation?.id && tab === 'history',
  });

  if (!installation) return null;

  const togglePermission = (perm) => {
    setPermissions((prev) => (prev.includes(perm) ? prev.filter((p) => p !== perm) : [...prev, perm]));
  };

  const handleConfigChange = (key, val) => setConfig((c) => ({ ...c, [key]: val }));

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/60" onClick={onClose}>
      <div
        className="w-full max-w-md h-full dark:bg-[#0c0c0e] border-l dark:border-white/10 overflow-y-auto p-6"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-start justify-between gap-4 mb-6">
          <div>
            <span className="text-2xl">{installation.agent_icon}</span>
            <h2 className="text-lg font-semibold mt-2">{installation.agent_name}</h2>
            <p className="text-xs dark:text-untold-muted">
              v{installation.installed_version}
              {installation.update_available && ` → v${installation.latest_version} available`}
            </p>
          </div>
          <button type="button" className="text-sm dark:text-untold-muted" onClick={onClose}>✕</button>
        </div>

        <div className="flex gap-1 mb-4 flex-wrap">
          {['config', 'permissions', 'memory', 'schedules', 'logs', 'analytics', 'history'].map((t) => (
            <button
              key={t}
              type="button"
              className={`studio-tab capitalize ${tab === t ? 'studio-tab--active' : ''}`}
              onClick={() => setTab(t)}
            >
              {t}
            </button>
          ))}
        </div>

        <div className="flex gap-2 mb-6 flex-wrap">
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
            <button type="button" className="studio-btn studio-btn--secondary text-xs" onClick={() => mutations.update.mutate(installation.id)}>
              Update to v{installation.latest_version}
            </button>
          )}
          <button
            type="button"
            className="studio-btn studio-btn--ghost text-xs text-red-400"
            onClick={() => {
              if (window.confirm('Uninstall this agent?')) mutations.uninstall.mutate(installation.id);
            }}
          >
            Uninstall
          </button>
        </div>

        {tab === 'config' && (
          <div className="space-y-3">
            {Object.entries(config).map(([key, val]) => (
              <ConfigField key={key} fieldKey={key} value={val} onChange={handleConfigChange} />
            ))}
            <button
              type="button"
              className="studio-btn studio-btn--primary text-xs w-full mt-4"
              onClick={() => mutations.configure.mutate({ id: installation.id, config })}
            >
              Save configuration
            </button>
          </div>
        )}

        {tab === 'permissions' && (
          <div className="space-y-2">
            <p className="text-xs dark:text-untold-muted mb-3">Grant capabilities this agent can use in your studio.</p>
            {(installation.available_permissions || []).map((perm) => (
              <label key={perm} className="flex items-center gap-2 text-xs py-1">
                <input type="checkbox" checked={permissions.includes(perm)} onChange={() => togglePermission(perm)} />
                <code className="text-untold-gold">{perm}</code>
              </label>
            ))}
            <button
              type="button"
              className="studio-btn studio-btn--primary text-xs w-full mt-4"
              onClick={() => mutations.permissions.mutate({ id: installation.id, granted_permissions: permissions })}
            >
              Save permissions
            </button>
          </div>
        )}

        {tab === 'history' && (
          <div className="space-y-2">
            {(history || []).map((item) => (
              <div key={item.id} className="text-xs py-2 border-b dark:border-white/5">
                <div className="flex justify-between gap-2">
                  <span className="uppercase text-untold-gold">{item.action}</span>
                  <span className="dark:text-untold-muted">{item.created_at?.slice(0, 10)}</span>
                </div>
                {item.from_version != null && (
                  <p className="dark:text-untold-muted mt-1">v{item.from_version} → v{item.to_version}</p>
                )}
                {item.notes && <p className="mt-1">{item.notes}</p>}
              </div>
            ))}
          </div>
        )}

        {tab === 'memory' && <AgentMemoryPanel installationId={installation.id} />}
        {tab === 'schedules' && <AgentSchedulesPanel installationId={installation.id} />}
        {tab === 'logs' && <AgentLogsPanel installationId={installation.id} />}
        {tab === 'analytics' && <AgentAnalyticsPanel installationId={installation.id} />}
      </div>
    </div>
  );
}

export default function AgentMarketplacePage() {
  const qc = useQueryClient();
  const [category, setCategory] = useState('all');
  const [pageTab, setPageTab] = useState('marketplace');
  const [manageAgent, setManageAgent] = useState(null);

  const invalidate = () => qc.invalidateQueries({ queryKey: marketplaceKey });

  const { data: overview, isLoading } = useQuery({
    queryKey: marketplaceKey,
    queryFn: () => studioPlatform.getAgentMarketplaceOverview(),
  });

  const mutations = {
    install: useMutation({
      mutationFn: (slug) => studioPlatform.installAgent(slug),
      onSuccess: invalidate,
    }),
    enable: useMutation({
      mutationFn: (id) => studioPlatform.enableAgent(id),
      onSuccess: invalidate,
    }),
    disable: useMutation({
      mutationFn: (id) => studioPlatform.disableAgent(id),
      onSuccess: invalidate,
    }),
    configure: useMutation({
      mutationFn: ({ id, config }) => studioPlatform.updateAgentConfig(id, { config }),
      onSuccess: invalidate,
    }),
    permissions: useMutation({
      mutationFn: ({ id, granted_permissions }) => studioPlatform.updateAgentPermissions(id, { granted_permissions }),
      onSuccess: invalidate,
    }),
    update: useMutation({
      mutationFn: (id) => studioPlatform.updateAgentVersion(id),
      onSuccess: invalidate,
    }),
    uninstall: useMutation({
      mutationFn: (id) => studioPlatform.uninstallAgent(id),
      onSuccess: () => {
        setManageAgent(null);
        invalidate();
      },
    }),
  };

  const agents = (overview?.agents || []).filter((a) => category === 'all' || a.category === category);
  const installation = manageAgent
    ? overview?.installations?.find((i) => i.agent_slug === manageAgent.slug || i.agent_id === manageAgent.id)
    : null;

  return (
    <div className="studio-page">
      <StudioPageHeader
        title="AI Agent Platform"
        description="Install agents from the marketplace, monitor runtime, memory, schedules, and execution logs"
      />

      <div className="flex gap-2 mt-4">
        {[
          { id: 'marketplace', label: 'Marketplace' },
          { id: 'monitoring', label: 'Monitoring' },
        ].map((t) => (
          <button
            key={t.id}
            type="button"
            className={`studio-tab ${pageTab === t.id ? 'studio-tab--active' : ''}`}
            onClick={() => setPageTab(t.id)}
          >
            {t.label}
          </button>
        ))}
      </div>

      {pageTab === 'monitoring' ? (
        <AgentMonitoringPanel />
      ) : isLoading ? (
        <p className="text-sm dark:text-untold-muted mt-6">Loading marketplace…</p>
      ) : (
        <>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-6">
            <div className="studio-card p-4">
              <div className="text-[10px] uppercase dark:text-untold-muted">Available</div>
              <div className="text-2xl font-semibold">{overview?.total_agents ?? 0}</div>
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
              <div className="text-[10px] uppercase dark:text-untold-muted">Updates</div>
              <div className="text-2xl font-semibold text-sky-400">{overview?.updates_available ?? 0}</div>
            </div>
          </div>

          <div className="flex gap-2 mt-6 flex-wrap">
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
            {agents.map((agent) => (
              <AgentCard
                key={agent.slug}
                agent={agent}
                onInstall={(a) => mutations.install.mutate(a.slug)}
                onManage={setManageAgent}
              />
            ))}
          </div>
        </>
      )}

      {manageAgent && (
        <ManageDrawer
          installation={installation}
          agent={manageAgent}
          onClose={() => setManageAgent(null)}
          mutations={mutations}
        />
      )}
    </div>
  );
}
