import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AppAuthContext';
import { useTheme } from '../../context/ThemeContext';
import { useWatchlist } from '../context/WatchlistContext';
import {
  UserIcon,
  SettingsIcon,
  BookmarkIcon,
  SunIcon,
  MoonIcon,
  CheckIcon,
} from '../../components/icons';

const menuItems = [
  { icon: BookmarkIcon, label: 'My List', action: 'watchlist' },
  { icon: SettingsIcon, label: 'Settings', action: 'settings' },
];

export default function ProfileScreen() {
  const { user, isAuthenticated, logout } = useAuth();
  const { isDark, toggleTheme, theme } = useTheme();
  const { items } = useWatchlist();
  const navigate = useNavigate();

  const handleMenu = (action) => {
    if (action === 'watchlist') navigate('/app/watchlist');
  };

  return (
    <div className="pb-4 animate-fade-in">
      <div className="px-4 pt-3 pb-2">
        <h1 className="text-xl font-display font-bold dark:text-untold-white light:text-black">Profile</h1>
      </div>

      <div className="px-4 mt-2">
        {/* Avatar & info */}
        <div className="flex items-center gap-4 p-4 rounded-2xl dark:bg-untold-surface light:bg-gray-50">
          <div className="w-16 h-16 rounded-full bg-gradient-to-br from-untold-gold to-untold-gold-dark flex items-center justify-center shrink-0">
            {isAuthenticated ? (
              <span className="text-2xl font-bold text-untold-dark">
                {user?.name?.[0]?.toUpperCase() || 'U'}
              </span>
            ) : (
              <UserIcon className="w-7 h-7 text-untold-dark" />
            )}
          </div>
          <div className="flex-1 min-w-0">
            <h2 className="text-lg font-semibold dark:text-untold-white light:text-black truncate">
              {isAuthenticated ? user?.name : 'Guest User'}
            </h2>
            <p className="text-sm dark:text-untold-muted light:text-gray-500 truncate">
              {isAuthenticated ? user?.email : 'Sign in to sync your watchlist'}
            </p>
            {isAuthenticated && (
              <span className="inline-flex items-center gap-1 mt-1.5 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-untold-gold/15 text-untold-gold">
                <CheckIcon className="w-3 h-3" />
                {user?.plan}
              </span>
            )}
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-3 mt-4">
          {[
            { label: 'Watchlist', value: items.length },
            { label: 'Watched', value: 12 },
            { label: 'Hours', value: '48' },
          ].map((stat) => (
            <div
              key={stat.label}
              className="text-center p-3 rounded-xl dark:bg-untold-surface/50 light:bg-gray-50"
            >
              <p className="text-lg font-bold text-untold-gold">{stat.value}</p>
              <p className="text-[10px] dark:text-untold-muted light:text-gray-400 mt-0.5">
                {stat.label}
              </p>
            </div>
          ))}
        </div>

        {/* Theme toggle */}
        <div className="mt-6">
          <p className="text-xs font-medium uppercase tracking-wider dark:text-untold-muted light:text-gray-400 mb-3 px-1">
            Appearance
          </p>
          <button
            onClick={toggleTheme}
            className="flex w-full items-center justify-between p-4 rounded-xl
              dark:bg-untold-surface light:bg-gray-50 active:scale-[0.99] transition-transform"
          >
            <div className="flex items-center gap-3">
              {isDark ? (
                <MoonIcon className="w-5 h-5 text-untold-gold" />
              ) : (
                <SunIcon className="w-5 h-5 text-untold-gold" />
              )}
              <span className="text-sm font-medium dark:text-untold-white light:text-black">
                {theme === 'dark' ? 'Dark Mode' : 'Light Mode'}
              </span>
            </div>
            <div className="w-11 h-6 rounded-full relative transition-colors bg-untold-gold/20">
              <div
                className={`absolute top-0.5 w-5 h-5 rounded-full bg-untold-gold transition-transform duration-300
                  ${isDark ? 'left-0.5' : 'left-[22px]'}`}
              />
            </div>
          </button>
        </div>

        {/* Menu */}
        <div className="mt-6">
          <p className="text-xs font-medium uppercase tracking-wider dark:text-untold-muted light:text-gray-400 mb-3 px-1">
            Account
          </p>
          <div className="rounded-xl overflow-hidden dark:bg-untold-surface light:bg-gray-50 divide-y dark:divide-untold-border light:divide-gray-100">
            {menuItems.map(({ icon: Icon, label, action }) => (
              <button
                key={label}
                onClick={() => handleMenu(action)}
                className="flex w-full items-center gap-3 px-4 py-3.5
                  active:dark:bg-white/5 active:light:bg-black/5 transition-colors"
              >
                <Icon className="w-5 h-5 dark:text-untold-muted light:text-gray-400" />
                <span className="text-sm dark:text-untold-white light:text-black">{label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Auth actions */}
        <div className="mt-6 space-y-3">
          {isAuthenticated ? (
            <button
              onClick={() => {
                logout();
                navigate('/app/login');
              }}
              className="w-full py-3 rounded-xl border dark:border-untold-border light:border-gray-200
                text-sm font-medium dark:text-untold-muted light:text-gray-500
                active:scale-[0.98] transition-transform"
            >
              Sign Out
            </button>
          ) : (
            <button
              onClick={() => navigate('/app/login')}
              className="w-full py-3 rounded-xl bg-untold-gold text-untold-dark text-sm font-semibold
                active:scale-[0.98] transition-transform"
            >
              Sign In
            </button>
          )}
        </div>

        <p className="text-center text-[10px] dark:text-untold-muted/50 light:text-gray-300 mt-8">
          UNTOLD v1.0.0
        </p>
      </div>
    </div>
  );
}
