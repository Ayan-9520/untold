import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { developerApi } from '../api/developerApi';

export default function HomePage() {
  const [account, setAccount] = useState(null);
  const [docs, setDocs] = useState(null);
  const [error, setError] = useState('');
  const [registering, setRegistering] = useState(false);

  useEffect(() => {
    developerApi.docs().then(setDocs).catch(() => {});
    developerApi
      .me()
      .then(setAccount)
      .catch((e) => {
        if (e.status !== 404) setError(String(e.message));
      });
  }, []);

  const register = async () => {
    setRegistering(true);
    setError('');
    try {
      const acc = await developerApi.register({});
      setAccount(acc);
    } catch (e) {
      setError(e.message || 'Registration failed — sign in first');
    } finally {
      setRegistering(false);
    }
  };

  return (
    <div className="space-y-8">
      <section>
        <h2 className="text-3xl font-bold">Build on UNTOLD</h2>
        <p className="mt-2 max-w-2xl text-neutral-400">
          REST API, GraphQL, webhooks, rate-limited API keys, sandbox environment, and usage analytics —
          everything you need to integrate UNTOLD into your products.
        </p>
      </section>

      {!account && (
        <div className="rounded-xl border border-neutral-800 bg-neutral-900/50 p-6">
          <h3 className="font-semibold">Get started</h3>
          <p className="mt-1 text-sm text-neutral-400">
            Sign in on UNTOLD, then register your developer account to create API keys.
          </p>
          <div className="mt-4 flex gap-3">
            <button
              type="button"
              onClick={register}
              disabled={registering}
              className="rounded-lg bg-rose-600 px-4 py-2 text-sm font-medium hover:bg-rose-500 disabled:opacity-50"
            >
              {registering ? 'Registering…' : 'Register developer account'}
            </button>
            <Link to="/login" className="rounded-lg border border-neutral-700 px-4 py-2 text-sm hover:bg-neutral-800">
              Sign in
            </Link>
          </div>
          {error && <p className="mt-3 text-sm text-red-400">{error}</p>}
        </div>
      )}

      {account && (
        <div className="grid gap-4 sm:grid-cols-3">
          <div className="rounded-xl border border-neutral-800 p-4">
            <div className="text-xs text-neutral-500">Account</div>
            <div className="mt-1 font-medium">{account.company_name || 'Developer'}</div>
            <div className="text-sm text-neutral-400">Tier: {account.tier}</div>
          </div>
          <div className="rounded-xl border border-neutral-800 p-4">
            <div className="text-xs text-neutral-500">Sandbox</div>
            <div className="mt-1 font-medium">{account.sandbox_enabled ? 'Enabled' : 'Disabled'}</div>
          </div>
          <div className="rounded-xl border border-neutral-800 p-4">
            <div className="text-xs text-neutral-500">Quick links</div>
            <div className="mt-2 flex flex-col gap-1 text-sm">
              <Link to="/developers/keys" className="text-rose-400 hover:underline">
                Create API key →
              </Link>
              <Link to="/developers/docs" className="text-rose-400 hover:underline">
                Read docs →
              </Link>
            </div>
          </div>
        </div>
      )}

      <section className="grid gap-4 md:grid-cols-2">
        {[
          { title: 'REST API', desc: 'Versioned JSON endpoints at /gateway/v1 and /gateway/v2' },
          { title: 'GraphQL', desc: 'Query videos and projects at /gateway/graphql' },
          { title: 'Webhooks', desc: 'Signed outbound events for video and project lifecycle' },
          { title: 'Sandbox', desc: 'Test with unt_sandbox_ keys — no production side effects' },
          { title: 'Rate limits', desc: 'Free, standard, and enterprise tiers per API key' },
          { title: 'SDK', desc: 'UntoldClient JavaScript SDK for REST and GraphQL' },
        ].map((f) => (
          <div key={f.title} className="rounded-lg border border-neutral-800/80 p-4">
            <h3 className="font-medium">{f.title}</h3>
            <p className="mt-1 text-sm text-neutral-400">{f.desc}</p>
          </div>
        ))}
      </section>

      {docs?.environments && (
        <section className="rounded-xl border border-neutral-800 bg-neutral-950 p-4 font-mono text-sm">
          <div className="text-neutral-500"># Production</div>
          <div>{docs.environments.production?.rest}</div>
          <div className="mt-3 text-neutral-500"># Sandbox</div>
          <div>{docs.environments.sandbox?.rest}</div>
        </section>
      )}
    </div>
  );
}
