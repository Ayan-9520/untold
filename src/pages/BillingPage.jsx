import { useEffect, useState } from 'react';
import { Link, Navigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import SEO from '../components/SEO';
import Button from '../components/ui/Button';
import { useWebAuth } from '../context/WebAuthContext';
import membershipApi from '../api/membership';
import client from '../api/client';

export default function BillingPage() {
  const { t } = useTranslation();
  const { user, isAuthenticated, loading } = useWebAuth();
  const [subscription, setSubscription] = useState(null);
  const [payments, setPayments] = useState([]);
  const [devices, setDevices] = useState([]);
  const [cancelling, setCancelling] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) return;
    membershipApi.getSubscription().then(setSubscription).catch(() => setSubscription({ plan: 'free', status: 'active', device_limit: 1 }));
    membershipApi.getPaymentHistory().then(setPayments).catch(() => setPayments([]));
    client.get('/mobile/devices').then((r) => setDevices(r.data || [])).catch(() => setDevices([]));
  }, [isAuthenticated]);

  const handleCancel = async () => {
    if (!window.confirm(t('billing.cancel'))) return;
    setCancelling(true);
    try {
      const result = await membershipApi.cancelSubscription();
      setSubscription((s) => ({ ...s, status: result.status }));
      alert(result.message);
    } catch (err) {
      alert(err.response?.data?.detail || t('billing.cancel'));
    } finally {
      setCancelling(false);
    }
  };

  if (loading) return null;
  if (!isAuthenticated) return <Navigate to="/login" state={{ from: { pathname: '/billing' } }} replace />;

  return (
    <>
      <SEO title={t('billing.title')} description={t('profile.billingDesc')} path="/billing" />
      <section className="profile-page pt-28 pb-16">
        <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8 space-y-8">
          <div>
            <Link to="/profile" className="text-sm text-untold-gold hover:underline">← {t('billing.backProfile')}</Link>
            <h1 className="font-display text-3xl font-bold text-white mt-4">{t('billing.title')}</h1>
            <p className="text-sm text-untold-muted mt-1">{user.email}</p>
          </div>

          <div className="profile-header-card">
            <div>
              <p className="text-xs uppercase tracking-widest text-untold-gold">{t('billing.currentPlan')}</p>
              <p className="text-2xl font-bold text-white capitalize mt-1">{subscription?.plan || 'free'}</p>
              <p className="text-sm text-untold-muted mt-1">{t('billing.status')}: {subscription?.status || 'active'}</p>
              {subscription?.expires_at && (
                <p className="text-sm text-untold-muted">{t('billing.renews')}: {new Date(subscription.expires_at).toLocaleDateString()}</p>
              )}
              <p className="text-sm text-untold-muted mt-2">{t('billing.deviceLimit')}: {subscription?.device_limit || 1}</p>
            </div>
            <div className="flex flex-wrap gap-2">
              <Link to="/membership"><Button variant="primary">{t('billing.changePlan')}</Button></Link>
              {subscription?.plan !== 'free' && subscription?.status === 'active' && (
                <Button variant="outline" disabled={cancelling} onClick={handleCancel}>
                  {cancelling ? t('billing.cancelling') : t('billing.cancel')}
                </Button>
              )}
            </div>
          </div>

          <div>
            <h2 className="profile-section-title">{t('billing.registeredDevices')} ({devices.length})</h2>
            {devices.length === 0 ? (
              <p className="text-sm text-untold-muted">{t('billing.noDevices')}</p>
            ) : (
              <ul className="space-y-2">
                {devices.map((d) => (
                  <li key={d.id} className="profile-history-row flex justify-between items-center">
                    <div>
                      <p className="text-sm font-medium text-white">{d.device_name || `${d.platform} device`}</p>
                      <p className="text-xs text-untold-muted">{d.app_type} · {d.platform}</p>
                    </div>
                    {d.last_seen_at && (
                      <span className="text-xs text-untold-muted">{t('billing.lastSeen')} {new Date(d.last_seen_at).toLocaleDateString()}</span>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div>
            <h2 className="profile-section-title">{t('billing.paymentHistory')}</h2>
            {payments.length === 0 ? (
              <p className="text-sm text-untold-muted">{t('billing.noPayments')}</p>
            ) : (
              <ul className="space-y-2">
                {payments.map((p) => (
                  <li key={p.id} className="profile-history-row flex justify-between items-center">
                    <div>
                      <p className="text-sm font-medium text-white capitalize">{p.plan_slug || 'payment'} · {p.provider}</p>
                      <p className="text-xs text-untold-muted">{new Date(p.created_at).toLocaleString()}</p>
                    </div>
                    <span className="text-sm text-untold-gold">{p.currency} {p.amount} · {p.status}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </section>
    </>
  );
}
