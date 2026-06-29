import { Link, Navigate } from 'react-router-dom';
import SEO from '../components/SEO';
import Badge from '../components/ui/Badge';
import FanDNACard from '../components/fan/FanDNACard';
import { useWebAuth } from '../context/WebAuthContext';
import { useLocale } from '../context/LocaleContext';

export default function Profile() {
  const { user, isAuthenticated, loading, logout } = useWebAuth();
  const { region, currency } = useLocale();

  if (loading) return null;
  if (!isAuthenticated) return <Navigate to="/login" state={{ from: { pathname: '/profile' } }} replace />;

  return (
    <>
      <SEO title="Profile" description="Your UNTOLD profile" path="/profile" />
      <section className="pt-28 pb-16">
        <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 space-y-8">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <p className="text-xs font-bold uppercase tracking-[0.3em] text-untold-gold mb-2">Member</p>
              <h1 className="font-display text-3xl font-bold dark:text-untold-white light:text-black">{user.full_name}</h1>
              <p className="text-sm dark:text-untold-muted light:text-gray-500 mt-1">{user.email}</p>
              <div className="flex flex-wrap gap-2 mt-3">
                <Badge variant="gold">Free Plan</Badge>
                <Badge variant="outline">{region}</Badge>
                <Badge variant="outline">{currency}</Badge>
              </div>
            </div>
            <div className="flex flex-wrap gap-2">
              <Link to="/watchlist" className="px-4 py-2 rounded-lg border dark:border-untold-border light:border-gray-200 text-sm font-medium hover:text-untold-gold">
                Watchlist
              </Link>
              <Link to="/membership" className="px-4 py-2 rounded-lg bg-untold-gold text-untold-dark text-sm font-semibold">
                Upgrade
              </Link>
              <button type="button" onClick={logout} className="px-4 py-2 rounded-lg text-sm text-red-400 hover:underline">
                Sign out
              </button>
            </div>
          </div>
          <FanDNACard />
        </div>
      </section>
    </>
  );
}
