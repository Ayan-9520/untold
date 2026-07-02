import { Link, Navigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import SEO from '../components/SEO';
import Badge from '../components/ui/Badge';
import ContentRow from '../components/ui/ContentRow';
import { useWebAuth } from '../context/WebAuthContext';
import { useLocale } from '../context/LocaleContext';
import { useEngagement } from '../context/EngagementContext';
import { useWatchlist } from '../context/WatchlistContext';
import membershipApi from '../api/membership';
import client from '../api/client';

export default function Profile() {
  const { t } = useTranslation();
  const { user, isAuthenticated, loading, logout } = useWebAuth();
  const { region, currency } = useLocale();
  const { continueWatching, watchHistory, clearHistory } = useEngagement();
  const { items: watchlist } = useWatchlist();
  const [subscription, setSubscription] = useState(null);
  const [deviceCount, setDeviceCount] = useState(0);

  useEffect(() => {
    if (!isAuthenticated) return;
    membershipApi.getSubscription().then(setSubscription).catch(() => setSubscription({ plan: 'free', device_limit: 1 }));
    client.get('/mobile/devices').then((r) => setDeviceCount((r.data || []).length)).catch(() => setDeviceCount(0));
  }, [isAuthenticated]);

  if (loading) return null;
  if (!isAuthenticated) return <Navigate to="/login" state={{ from: { pathname: '/profile' } }} replace />;

  const planLabel = subscription?.plan ? subscription.plan.charAt(0).toUpperCase() + subscription.plan.slice(1) : 'Free';

  return (
    <>
      <SEO title={t('profile.myProfile')} description={t('brand.description')} path="/profile" />
      <section className="profile-page pt-28 pb-16">
        <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 space-y-10">
          {/* Header */}
          <div className="profile-header-card">
            <div>
              <p className="text-xs font-bold uppercase tracking-[0.35em] text-untold-gold mb-2">UNTOLD ORIGINALS</p>
              <h1 className="font-display text-3xl sm:text-4xl font-bold text-white">{user.full_name}</h1>
              <p className="text-sm text-untold-muted mt-1">{user.email}</p>
              <div className="flex flex-wrap gap-2 mt-4">
                <Badge variant="gold">{planLabel} {t('profile.plan')}</Badge>
                <Badge variant="outline">{region?.label || region}</Badge>
                <Badge variant="outline">{currency}</Badge>
              </div>
            </div>
            <div className="flex flex-wrap gap-2 items-start">
              <Link to="/billing" className="profile-action-btn profile-action-btn--gold">{t('profile.billing')}</Link>
              <Link to="/membership" className="profile-action-btn profile-action-btn--muted">{t('profile.upgrade')}</Link>
              <button type="button" onClick={logout} className="profile-action-btn profile-action-btn--muted">{t('profile.signOut')}</button>
            </div>
          </div>

          {/* Quick stats */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {[
              { label: t('profile.watchlist'), value: watchlist.length, to: '/watchlist' },
              { label: t('profile.inProgress'), value: continueWatching.length, to: '#continue' },
              { label: t('profile.history'), value: watchHistory.length, to: '#history' },
              { label: t('profile.devices'), value: deviceCount || subscription?.device_limit || 1, to: '/billing' },
            ].map((stat) => (
              <Link key={stat.label} to={stat.to} className="profile-stat-card">
                <p className="text-2xl font-bold text-untold-gold">{stat.value}</p>
                <p className="text-xs text-untold-muted mt-1 uppercase tracking-wider">{stat.label}</p>
              </Link>
            ))}
          </div>

          {/* Continue watching */}
          {continueWatching.length > 0 && (
            <div id="continue">
              <h2 className="profile-section-title">{t('profile.continueWatching')}</h2>
              <ContentRow>
                {continueWatching.map((item) => (
                  <Link key={item.id} to={`/video/${item.id}`} className="ott-continue-card shrink-0 w-[200px]">
                    <div className="relative aspect-video rounded-lg overflow-hidden border border-untold-border">
                      <img src={item.image} alt="" className="h-full w-full object-cover" loading="lazy" />
                      <div className="absolute bottom-0 left-0 right-0 h-1 bg-white/15">
                        <div className="h-full bg-untold-gold" style={{ width: `${item.progress * 100}%` }} />
                      </div>
                    </div>
                    <p className="mt-2 text-sm font-medium text-white line-clamp-2">{item.title}</p>
                  </Link>
                ))}
              </ContentRow>
            </div>
          )}

          {/* History */}
          {watchHistory.length > 0 && (
            <div id="history">
              <div className="flex items-center justify-between mb-4">
                <h2 className="profile-section-title mb-0">{t('profile.watchHistory')}</h2>
                <button type="button" onClick={clearHistory} className="text-xs text-untold-muted hover:text-untold-gold">
                  {t('profile.clearAll')}
                </button>
              </div>
              <ul className="space-y-2">
                {watchHistory.map((item) => (
                  <li key={item.id}>
                    <Link to={`/video/${item.id}`} className="profile-history-row">
                      <img src={item.image} alt="" className="w-16 h-10 rounded object-cover shrink-0" />
                      <span className="flex-1 text-sm text-white truncate">{item.title}</span>
                      <span className="text-xs text-untold-muted">{Math.round(item.progress * 100)}%</span>
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Account links */}
          <div className="grid sm:grid-cols-2 gap-3">
            {[
              { to: '/watchlist', title: t('profile.myWatchlist'), desc: t('profile.watchlistDesc') },
              { to: '/settings', title: t('profile.settings'), desc: t('profile.settingsDesc') },
              { to: '/billing', title: t('billing.title'), desc: t('profile.billingDesc') },
              { to: '/help', title: t('profile.help'), desc: t('profile.helpDesc') },
              { to: '/app', title: t('profile.mobileApp'), desc: t('profile.mobileDesc') },
              { to: '/about', title: t('profile.about'), desc: t('profile.aboutDesc') },
            ].map((link) => (
              <Link key={link.to} to={link.to} className="profile-link-card">
                <p className="font-semibold text-white">{link.title}</p>
                <p className="text-sm text-untold-muted mt-1">{link.desc}</p>
              </Link>
            ))}
          </div>
        </div>
      </section>
    </>
  );
}
