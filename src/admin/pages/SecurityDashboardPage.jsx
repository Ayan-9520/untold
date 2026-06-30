import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import StudioPageHeader from '../components/StudioPageHeader';
import { studioPlatform } from '../api/adminApi';

const securityKey = ['enterprise-security'];

function Stat({ label, value, accent }) {
  return (
    <div className="studio-card p-4">
      <div className="text-[10px] uppercase dark:text-untold-muted">{label}</div>
      <div className={`text-2xl font-semibold mt-1 ${accent || ''}`}>{value}</div>
    </div>
  );
}

export default function SecurityDashboardPage() {
  const [tab, setTab] = useState('overview');
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: securityKey,
    queryFn: async () => {
      const [overview, compliance, idp, audit, sessions, ipRules, secrets, rbac, mfa] = await Promise.all([
        studioPlatform.getSecurityOverview(),
        studioPlatform.getSecurityCompliance(),
        studioPlatform.listIdpProviders(),
        studioPlatform.getSecurityAudit(),
        studioPlatform.listSecuritySessions(),
        studioPlatform.listSecurityIpRules(),
        studioPlatform.listSecuritySecrets(),
        studioPlatform.getSecurityRbac(),
        studioPlatform.getMfaStatus(),
      ]);
      return { overview, compliance, idp, audit, sessions, ipRules, secrets, rbac, mfa };
    },
  });

  const invalidate = () => queryClient.invalidateQueries({ queryKey: securityKey });

  const [ipName, setIpName] = useState('');
  const [ipCidr, setIpCidr] = useState('');
  const [ipType, setIpType] = useState('allow');
  const [secretName, setSecretName] = useState('');
  const [secretKey, setSecretKey] = useState('');
  const [secretValue, setSecretValue] = useState('');
  const [mfaCode, setMfaCode] = useState('');
  const [mfaSetup, setMfaSetup] = useState(null);

  const createIpRule = useMutation({
    mutationFn: (payload) => studioPlatform.createSecurityIpRule(payload),
    onSuccess: () => { setIpName(''); setIpCidr(''); invalidate(); },
  });
  const deleteIpRule = useMutation({
    mutationFn: (id) => studioPlatform.deleteSecurityIpRule(id),
    onSuccess: invalidate,
  });
  const createSecret = useMutation({
    mutationFn: (payload) => studioPlatform.createSecuritySecret(payload),
    onSuccess: () => { setSecretName(''); setSecretKey(''); setSecretValue(''); invalidate(); },
  });
  const deleteSecret = useMutation({
    mutationFn: (id) => studioPlatform.deleteSecuritySecret(id),
    onSuccess: invalidate,
  });
  const revokeSession = useMutation({
    mutationFn: (id) => studioPlatform.revokeSecuritySession(id),
    onSuccess: invalidate,
  });
  const setupMfa = useMutation({
    mutationFn: () => studioPlatform.setupMfa(),
    onSuccess: (res) => setMfaSetup(res),
  });
  const verifyMfa = useMutation({
    mutationFn: (code) => studioPlatform.verifyMfaSetup(code),
    onSuccess: () => { setMfaSetup(null); setMfaCode(''); invalidate(); },
  });
  const toggleIdp = useMutation({
    mutationFn: ({ slug, enabled }) => studioPlatform.updateIdpProvider(slug, { enabled }),
    onSuccess: invalidate,
  });

  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'sso', label: 'SSO / OAuth / SAML' },
    { id: 'mfa', label: '2FA' },
    { id: 'rbac', label: 'RBAC' },
    { id: 'audit', label: 'Audit Logs' },
    { id: 'sessions', label: 'Sessions' },
    { id: 'ip', label: 'IP Rules' },
    { id: 'secrets', label: 'Secrets' },
    { id: 'compliance', label: 'Compliance' },
  ];

  const ov = data?.overview;

  return (
    <div className="studio-page">
      <StudioPageHeader
        title="Enterprise Security"
        description="SSO, OAuth, SAML, 2FA, RBAC, audit logs, encryption, secrets, sessions, and IP restrictions"
      />

      <div className="flex gap-2 mt-6 flex-wrap">
        {tabs.map((t) => (
          <button
            key={t.id}
            type="button"
            className={`px-3 py-1.5 rounded-full text-xs ${
              tab === t.id ? 'bg-untold-gold/20 text-untold-gold' : 'dark:text-untold-muted hover:bg-white/5'
            }`}
            onClick={() => setTab(t.id)}
          >
            {t.label}
          </button>
        ))}
      </div>

      {isLoading ? (
        <p className="text-sm dark:text-untold-muted mt-6">Loading security dashboard…</p>
      ) : (
        <div className="mt-6 space-y-6">
          {tab === 'overview' && (
            <>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <Stat label="MFA Enrolled" value={ov?.mfa_enrolled_users ?? 0} accent="text-emerald-400" />
                <Stat label="Active Sessions" value={ov?.active_sessions ?? 0} />
                <Stat label="IdP Enabled" value={ov?.idp_providers_enabled ?? 0} />
                <Stat label="Compliance" value={`${ov?.compliance_score ?? 0}%`} accent="text-untold-gold" />
              </div>
              <div className="grid md:grid-cols-2 gap-4">
                <div className="studio-card p-4 text-sm dark:text-untold-muted">
                  <p><strong className="text-white">Audit events (24h):</strong> {ov?.audit_events_24h}</p>
                  <p className="mt-2"><strong className="text-white">Security events (24h):</strong> {ov?.security_events_24h}</p>
                  <p className="mt-2"><strong className="text-white">IP rules:</strong> {ov?.ip_rules_count}</p>
                  <p className="mt-2"><strong className="text-white">Secrets vault:</strong> {ov?.secrets_count}</p>
                </div>
                <div className="studio-card p-4">
                  <h3 className="text-sm font-semibold mb-2">Compliance status</h3>
                  <p className={`text-lg font-semibold ${ov?.compliance_status === 'compliant' ? 'text-emerald-400' : 'text-amber-400'}`}>
                    {ov?.compliance_status}
                  </p>
                </div>
              </div>
            </>
          )}

          {tab === 'sso' && (
            <div className="studio-card divide-y dark:divide-white/5">
              {(data?.idp || []).map((p) => (
                <div key={p.slug} className="p-4 flex flex-wrap justify-between gap-2">
                  <div>
                    <div className="font-medium">{p.name}</div>
                    <code className="text-xs text-untold-gold">{p.provider_type}</code>
                    <p className="text-xs dark:text-untold-muted mt-1">{p.issuer_url || p.saml_sso_url || '—'}</p>
                  </div>
                  <button
                    type="button"
                    className={`text-xs ${p.enabled ? 'text-emerald-400' : 'text-untold-muted'}`}
                    onClick={() => toggleIdp.mutate({ slug: p.slug, enabled: !p.enabled })}
                  >
                    {p.enabled ? 'Enabled' : 'Enable'}
                  </button>
                </div>
              ))}
            </div>
          )}

          {tab === 'mfa' && (
            <div className="studio-card p-4 space-y-4">
              <p className="text-sm dark:text-untold-muted">
                Status: <strong className={data?.mfa?.enabled ? 'text-emerald-400' : 'text-amber-400'}>
                  {data?.mfa?.enabled ? 'Enabled' : 'Not enabled'}
                </strong>
              </p>
              {!data?.mfa?.enabled && !mfaSetup && (
                <button type="button" className="studio-btn studio-btn--primary text-xs" onClick={() => setupMfa.mutate()}>
                  Set up authenticator app
                </button>
              )}
              {mfaSetup && (
                <div className="space-y-3 text-xs">
                  <p className="dark:text-untold-muted">Scan QR or enter secret in your authenticator app:</p>
                  <code className="block break-all">{mfaSetup.provisioning_uri}</code>
                  <p className="text-amber-400">Save backup codes: {mfaSetup.backup_codes?.join(', ')}</p>
                  <div className="flex gap-2">
                    <input className="studio-input" placeholder="6-digit code" value={mfaCode} onChange={(e) => setMfaCode(e.target.value)} />
                    <button type="button" className="studio-btn studio-btn--primary text-xs" onClick={() => verifyMfa.mutate(mfaCode)}>Verify</button>
                  </div>
                </div>
              )}
            </div>
          )}

          {tab === 'rbac' && (
            <div className="studio-card divide-y dark:divide-white/5 max-h-96 overflow-y-auto">
              {(data?.rbac || []).map((r) => (
                <div key={r.permission} className="p-3 text-xs flex justify-between gap-2">
                  <code className="text-untold-gold">{r.permission}</code>
                  <span className="dark:text-untold-muted">{r.roles?.join(', ')}</span>
                </div>
              ))}
            </div>
          )}

          {tab === 'audit' && (
            <div className="studio-card divide-y dark:divide-white/5 max-h-[28rem] overflow-y-auto">
              {(data?.audit || []).map((e) => (
                <div key={e.id} className="p-3 text-xs">
                  <div className="flex justify-between">
                    <code className="text-untold-gold">{e.action}</code>
                    <span className={e.severity === 'warn' ? 'text-amber-400' : 'dark:text-untold-muted'}>{e.severity}</span>
                  </div>
                  <p className="dark:text-untold-muted mt-1">{e.actor_email} · {e.ip_address || '—'}</p>
                  {(e.compliance_tags || []).length > 0 && (
                    <p className="text-[10px] mt-1">{e.compliance_tags.join(' · ')}</p>
                  )}
                </div>
              ))}
            </div>
          )}

          {tab === 'sessions' && (
            <div className="studio-card divide-y dark:divide-white/5">
              {(data?.sessions || []).map((s) => (
                <div key={s.id} className="p-3 flex justify-between text-xs">
                  <div>
                    <code>{s.session_id}</code>
                    <p className="dark:text-untold-muted">{s.auth_method} · {s.ip_address}</p>
                  </div>
                  {s.is_active && (
                    <button type="button" className="text-red-400" onClick={() => revokeSession.mutate(s.id)}>Revoke</button>
                  )}
                </div>
              ))}
            </div>
          )}

          {tab === 'ip' && (
            <>
              <div className="studio-card p-4 flex flex-wrap gap-2">
                <input className="studio-input" placeholder="Rule name" value={ipName} onChange={(e) => setIpName(e.target.value)} />
                <input className="studio-input" placeholder="CIDR e.g. 10.0.0.0/8" value={ipCidr} onChange={(e) => setIpCidr(e.target.value)} />
                <select className="studio-input" value={ipType} onChange={(e) => setIpType(e.target.value)}>
                  <option value="allow">Allow</option>
                  <option value="deny">Deny</option>
                </select>
                <button
                  type="button"
                  className="studio-btn studio-btn--primary text-xs"
                  disabled={!ipName || !ipCidr}
                  onClick={() => createIpRule.mutate({ name: ipName, cidr: ipCidr, rule_type: ipType })}
                >
                  Add rule
                </button>
              </div>
              <div className="studio-card divide-y dark:divide-white/5">
                {(data?.ipRules || []).map((r) => (
                  <div key={r.id} className="p-3 flex justify-between text-xs">
                    <span><strong>{r.name}</strong> — {r.rule_type} {r.cidr}</span>
                    <button type="button" className="text-red-400" onClick={() => deleteIpRule.mutate(r.id)}>Delete</button>
                  </div>
                ))}
              </div>
            </>
          )}

          {tab === 'secrets' && (
            <>
              <div className="studio-card p-4 grid sm:grid-cols-3 gap-2">
                <input className="studio-input" placeholder="Display name" value={secretName} onChange={(e) => setSecretName(e.target.value)} />
                <input className="studio-input" placeholder="Key e.g. STRIPE_WEBHOOK" value={secretKey} onChange={(e) => setSecretKey(e.target.value)} />
                <input className="studio-input" placeholder="Value" type="password" value={secretValue} onChange={(e) => setSecretValue(e.target.value)} />
                <button
                  type="button"
                  className="studio-btn studio-btn--primary text-xs sm:col-span-3"
                  disabled={!secretName || !secretKey || !secretValue}
                  onClick={() => createSecret.mutate({ name: secretName, secret_key: secretKey, value: secretValue, rotation_days: 90 })}
                >
                  Store encrypted secret
                </button>
              </div>
              <div className="studio-card divide-y dark:divide-white/5">
                {(data?.secrets || []).map((s) => (
                  <div key={s.id} className="p-3 flex justify-between text-xs">
                    <span>{s.name} — <code>{s.secret_key}</code> v{s.version}</span>
                    <button type="button" className="text-red-400" onClick={() => deleteSecret.mutate(s.id)}>Delete</button>
                  </div>
                ))}
              </div>
            </>
          )}

          {tab === 'compliance' && data?.compliance && (
            <div className="space-y-4">
              <div className="studio-card p-4">
                <div className="text-3xl font-bold text-untold-gold">{data.compliance.score}%</div>
                <p className="text-sm dark:text-untold-muted mt-1">Frameworks: {data.compliance.frameworks?.join(', ')}</p>
              </div>
              <div className="grid sm:grid-cols-2 gap-3">
                {(data.compliance.controls || []).map((c) => (
                  <div key={c.id} className="studio-card p-4 text-sm">
                    <div className="flex justify-between">
                      <span className="font-medium">{c.label}</span>
                      <span className={c.status === 'pass' ? 'text-emerald-400' : 'text-amber-400'}>{c.status}</span>
                    </div>
                    <p className="text-xs dark:text-untold-muted mt-2">{c.detail}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
