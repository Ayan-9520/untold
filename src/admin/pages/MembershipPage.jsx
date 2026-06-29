import { useState, useEffect } from 'react';
import DataTable from '../components/DataTable';
import StatCard from '../components/StatCard';
import { membership } from '../api/adminApi';
import { MEMBERSHIP_PLANS, REVENUE_STREAMS, getPlanPricing } from '../../data/revenueStrategy';
import { CURRENCIES } from '../../data/regionalConfig';
import { DollarSignIcon, UsersIcon } from '../components/AdminIcons';

const MOCK_STATS = {
  total_subscribers: 12840,
  premium_count: 4520,
  vip_count: 890,
  free_count: 7430,
  mrr: 28450,
  currency: 'USD',
};

export default function MembershipPage() {
  const [stats, setStats] = useState(MOCK_STATS);
  const [currency, setCurrency] = useState('USD');
  const [subscriptions, setSubscriptions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [usingMock, setUsingMock] = useState(false);

  useEffect(() => {
    membership.getStats()
      .then((d) => { setStats(d); setUsingMock(false); })
      .catch(() => { setStats(MOCK_STATS); setUsingMock(true); })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    membership.listSubscriptions({ page: 1, page_size: 10 })
      .then((data) => setSubscriptions(data.items || []))
      .catch(() => setSubscriptions([]));
  }, []);

  const plans = getPlanPricing(currency);

  const columns = [
    { key: 'user_email', label: 'User', render: (row) => row.user_email || row.email || '—' },
    { key: 'plan', label: 'Plan', render: (row) => <span className="capitalize font-medium text-untold-gold">{row.plan}</span> },
    { key: 'status', label: 'Status', render: (row) => <span className="capitalize text-xs">{row.status}</span> },
    { key: 'started_at', label: 'Since', render: (row) => row.started_at ? new Date(row.started_at).toLocaleDateString() : '—' },
  ];

  return (
    <div className="space-y-8 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold dark:text-untold-white light:text-black">Membership</h1>
        <p className="text-sm dark:text-untold-muted light:text-gray-500 mt-1">
          Manage plans, pricing, and subscriber tiers — Free · Premium · VIP
        </p>
      </div>

      {usingMock && (
        <p className="text-xs px-3 py-2 rounded-lg bg-amber-500/10 text-amber-300 border border-amber-500/20">
          Showing sample membership stats — connect backend for live subscriber data.
        </p>
      )}

      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Total Subscribers" value={stats.total_subscribers?.toLocaleString() || '—'} icon={UsersIcon} accent="gold" />
        <StatCard title="Premium" value={stats.premium_count?.toLocaleString() || '—'} icon={UsersIcon} accent="blue" />
        <StatCard title="VIP" value={stats.vip_count?.toLocaleString() || '—'} icon={UsersIcon} accent="purple" />
        <StatCard title="MRR" value={`$${stats.mrr?.toLocaleString() || '0'}`} icon={DollarSignIcon} accent="green" />
      </div>

      <div className="flex flex-wrap gap-2">
        {CURRENCIES.map((c) => (
          <button
            key={c.code}
            type="button"
            onClick={() => setCurrency(c.code)}
            className={`px-4 py-2 rounded-full text-sm font-medium transition-colors
              ${currency === c.code
                ? 'bg-untold-gold text-untold-dark'
                : 'dark:bg-white/5 light:bg-gray-100 dark:text-untold-muted light:text-gray-600'
              }`}
          >
            {c.label}
          </button>
        ))}
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        {plans.map((plan) => (
          <div
            key={plan.id}
            className={`rounded-xl p-6 border
              ${plan.popular ? 'border-untold-gold dark:bg-untold-gold/5' : 'dark:border-white/10 light:border-gray-200'}`}
          >
            <h3 className="font-display text-lg font-bold dark:text-untold-white light:text-black">{plan.name}</h3>
            <p className="mt-2 text-2xl font-bold text-untold-gold">
              {plan.currencySymbol}{plan.monthlyPrice}
              <span className="text-sm font-normal dark:text-untold-muted light:text-gray-500">/mo</span>
            </p>
            <ul className="mt-4 space-y-2">
              {plan.features.map((f) => (
                <li key={f} className="text-sm dark:text-untold-muted light:text-gray-600 flex gap-2">
                  <span className="text-untold-gold">✓</span> {f}
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>

      <div>
        <h2 className="text-lg font-semibold dark:text-untold-white light:text-black mb-4">Revenue Streams</h2>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {REVENUE_STREAMS.map((stream) => (
            <div key={stream.id} className="rounded-xl p-4 border dark:border-white/10 light:border-gray-200 dark:bg-untold-surface/50">
              <span className="text-2xl">{stream.icon}</span>
              <h3 className="mt-2 font-semibold dark:text-untold-white light:text-black">{stream.label}</h3>
              <p className="text-xs dark:text-untold-muted light:text-gray-500 mt-1">{stream.description}</p>
            </div>
          ))}
        </div>
      </div>

      <div>
        <h2 className="text-lg font-semibold dark:text-untold-white light:text-black mb-4">Recent Subscriptions</h2>
        {loading ? (
          <div className="h-48 rounded-xl skeleton" />
        ) : (
          <DataTable columns={columns} data={subscriptions} emptyMessage="No subscriptions yet — connect backend to sync" />
        )}
      </div>
    </div>
  );
}
