import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import StudioPageHeader from '../components/StudioPageHeader';
import { studioPlatform } from '../api/adminApi';

const complianceKey = ['enterprise-compliance'];

export default function CompliancePage() {
  const [tab, setTab] = useState('report');
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: complianceKey,
    queryFn: async () => {
      const [report, policies, consents, privacyRequests, accessLogs] = await Promise.all([
        studioPlatform.getComplianceReport(),
        studioPlatform.listCompliancePolicies(),
        studioPlatform.listComplianceConsents(),
        studioPlatform.listPrivacyRequests(),
        studioPlatform.listComplianceAccessLogs({ limit: 100 }),
      ]);
      return { report, policies, consents, privacyRequests, accessLogs };
    },
  });

  const invalidate = () => queryClient.invalidateQueries({ queryKey: complianceKey });

  const runRetention = useMutation({
    mutationFn: () => studioPlatform.runComplianceRetention(),
    onSuccess: invalidate,
  });

  const processErasure = useMutation({
    mutationFn: (id) => studioPlatform.processPrivacyErasure(id),
    onSuccess: invalidate,
  });

  const exportData = useMutation({
    mutationFn: (id) => studioPlatform.exportPrivacyData(id),
    onSuccess: invalidate,
  });

  const tabs = [
    { id: 'report', label: 'Compliance Report' },
    { id: 'policies', label: 'Data Retention' },
    { id: 'consent', label: 'Consent' },
    { id: 'privacy', label: 'Privacy Requests' },
    { id: 'access', label: 'Access Logs' },
  ];

  return (
    <div>
      <StudioPageHeader
        title="Enterprise Compliance"
        description="GDPR, SOC2, ISO27001 — consent, retention, privacy requests, and access monitoring."
      />

      <div className="mt-6 flex flex-wrap gap-2">
        {tabs.map((t) => (
          <button
            key={t.id}
            type="button"
            onClick={() => setTab(t.id)}
            className={`rounded-lg px-3 py-1.5 text-sm ${
              tab === t.id ? 'bg-rose-600 text-white' : 'bg-neutral-800 text-neutral-300'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {isLoading && <p className="mt-6 text-sm dark:text-untold-muted">Loading compliance data…</p>}

      {!isLoading && tab === 'report' && data?.report && (
        <div className="mt-6 space-y-4">
          <div className="studio-card p-6">
            <div className="text-4xl font-bold text-untold-gold">{data.report.score}%</div>
            <p className="text-sm dark:text-untold-muted mt-1">Status: {data.report.status}</p>
            <p className="text-xs dark:text-untold-muted mt-2">
              Frameworks: {data.report.frameworks?.join(', ')}
            </p>
            {data.report.metrics && (
              <div className="mt-4 grid gap-3 sm:grid-cols-4 text-sm">
                <div>Consents (30d): {data.report.metrics.consent_events_30d}</div>
                <div>Open DSARs: {data.report.metrics.pending_privacy_requests}</div>
                <div>Access logs (24h): {data.report.metrics.access_logs_24h}</div>
                <div>Policies: {data.report.metrics.retention_policies}</div>
              </div>
            )}
          </div>
          <ul className="space-y-2">
            {(data.report.controls || []).map((c) => (
              <li key={c.id} className="studio-card flex justify-between p-3 text-sm">
                <div>
                  <div className="font-medium">{c.label}</div>
                  <div className="text-xs dark:text-untold-muted">{c.detail}</div>
                  <div className="text-[10px] mt-1 text-neutral-500">{(c.frameworks || []).join(' · ')}</div>
                </div>
                <span className={c.status === 'pass' ? 'text-emerald-400' : 'text-amber-400'}>{c.status}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {tab === 'policies' && (
        <div className="mt-6">
          <div className="mb-4 flex items-center justify-between">
            <h3 className="font-medium">Retention policies</h3>
            <button
              type="button"
              onClick={() => runRetention.mutate()}
              disabled={runRetention.isPending}
              className="rounded-lg bg-neutral-800 px-3 py-1.5 text-sm"
            >
              Run purge now
            </button>
          </div>
          <ul className="space-y-2">
            {(data?.policies || []).map((p) => (
              <li key={p.policy_key} className="studio-card p-4 text-sm">
                <div className="font-medium">{p.name}</div>
                <div className="text-xs dark:text-untold-muted">{p.description}</div>
                <div className="mt-2 flex flex-wrap gap-3 text-xs">
                  <span>{p.retention_days} days</span>
                  <span>{p.legal_basis}</span>
                  <span>{p.auto_purge ? 'auto-purge' : 'retain'}</span>
                  <span>{(p.frameworks || []).join(', ')}</span>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}

      {tab === 'consent' && (
        <ul className="mt-6 space-y-2">
          {(data?.consents || []).map((c) => (
            <li key={c.id} className="studio-card p-3 text-sm flex justify-between">
              <div>
                <div>{c.subject_email || `user #${c.user_id}`}</div>
                <div className="text-xs dark:text-untold-muted">
                  {c.consent_type} · v{c.policy_version} · {c.source}
                </div>
              </div>
              <span className={c.granted ? 'text-emerald-400' : 'text-red-400'}>
                {c.granted ? 'granted' : 'denied'}
              </span>
            </li>
          ))}
        </ul>
      )}

      {tab === 'privacy' && (
        <ul className="mt-6 space-y-2">
          {(data?.privacyRequests || []).map((r) => (
            <li key={r.id} className="studio-card p-4 text-sm">
              <div className="flex justify-between">
                <div>
                  <div className="font-medium">{r.request_type}</div>
                  <div className="text-xs dark:text-untold-muted">{r.subject_email}</div>
                  <div className="text-xs mt-1">Status: {r.status}</div>
                </div>
                <div className="flex gap-2">
                  {r.request_type === 'erasure' && r.status === 'pending' && (
                    <button
                      type="button"
                      onClick={() => processErasure.mutate(r.id)}
                      className="text-red-400 text-xs"
                    >
                      Process erasure
                    </button>
                  )}
                  {r.request_type in { access: 1, portability: 1 } && r.status === 'pending' && (
                    <button
                      type="button"
                      onClick={() => exportData.mutate(r.id)}
                      className="text-rose-400 text-xs"
                    >
                      Export data
                    </button>
                  )}
                </div>
              </div>
            </li>
          ))}
        </ul>
      )}

      {tab === 'access' && (
        <div className="mt-6 overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="dark:text-untold-muted">
                <th className="p-2">Time</th>
                <th className="p-2">User</th>
                <th className="p-2">Method</th>
                <th className="p-2">Path</th>
                <th className="p-2">Status</th>
                <th className="p-2">IP</th>
              </tr>
            </thead>
            <tbody>
              {(data?.accessLogs || []).map((l) => (
                <tr key={l.id} className="border-t border-neutral-800">
                  <td className="p-2">{l.created_at ? new Date(l.created_at).toLocaleString() : '—'}</td>
                  <td className="p-2">{l.user_email || '—'}</td>
                  <td className="p-2">{l.method}</td>
                  <td className="p-2 max-w-xs truncate">{l.path}</td>
                  <td className="p-2">{l.status_code}</td>
                  <td className="p-2">{l.ip_address}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
