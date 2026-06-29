import { Link, Navigate } from 'react-router-dom';
import SEO from '../components/SEO';
import Badge from '../components/ui/Badge';
import ContentRow from '../components/ui/ContentRow';
import { useWebAuth } from '../context/WebAuthContext';
import { useLocale } from '../context/LocaleContext';
import { useEngagement } from '../context/EngagementContext';
import { useWatchlist } from '../context/WatchlistContext';

export default function Profile() {
  const { user, isAuthenticated, loading, logout } = useWebAuth();
  const { region, currency } = useLocale();
  const { continueWatching, watchHistory, clearHistory } = useEngagement();
  const { items: watchlist } = useWatchlist();

  if (loading) return null;
  if (!isAuthenticated) return <Navigate to="/login" state={{ from: { pathname: '/profile' } }} replace />;

  return (
    <>
      <SEO title="My Profile" description="Your UNTOLD ORIGINALS account — watchlist, history, and subscription." path="/profile" />
      <section className="profile-page pt-28 pb-16">
        <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 space-y-10">
          {/* Header */}
          <div className="profile-header-card">
            <div>
              <p className="text-xs font-bold uppercase tracking-[0.35em] text-untold-gold mb-2">UNTOLD ORIGINALS</p>
              <h1 className="font-display text-3xl sm:text-4xl font-bold text-white">{user.full_name}</h1>
              <p className="text-sm text-untold-muted mt-1">{user.email}</p>
              <div className="flex flex-wrap gap-2 mt-4">
                <Badge variant="gold">Member</Badge>
                <Badge variant="outline">{region?.label || region}</Badge>
                <Badge variant="outline">{currency}</Badge>
              </div>
            </div>
            <div className="flex flex-wrap gap-2">
              <Link to="/membership" className="profile-action-btn profile-action-btn--gold">Upgrade Plan</Link>
              <button type="button" onClick={logout} className="profile-action-btn profile-action-btn--muted">Sign out</button>
            </div>
          </div>

          {/* Quick stats */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {[
              { label: 'Watchlist', value: watchlist.length, to: '/watchlist' },
              { label: 'In Progress', value: continueWatching.length, to: '#continue' },
              { label: 'History', value: watchHistory.length, to: '#history' },
              { label: 'Devices', value: '1', to: '/membership' },
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
              <h2 className="profile-section-title">Continue Watching</h2>
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
                <h2 className="profile-section-title mb-0">Watch History</h2>
                <button type="button" onClick={clearHistory} className="text-xs text-untold-muted hover:text-untold-gold">
                  Clear all
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
              { to: '/watchlist', title: 'My Watchlist', desc: 'Saved documentaries & series' },
              { to: '/membership', title: 'Subscription', desc: 'Plans, billing & benefits' },
              { to: '/app', title: 'Mobile App', desc: 'Watch on your phone' },
              { to: '/about', title: 'About UNTOLD', desc: 'Our story & mission' },
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
