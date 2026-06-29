import { Link, NavLink, useLocation } from 'react-router-dom';
import Logo from '../../components/brand/Logo';
import { SearchIcon, BellIcon, SunIcon, MoonIcon } from '../../components/icons';
import { useAppUI } from '../context/AppUIContext';
import { useTheme } from '../../context/ThemeContext';

const scrollLinks = [
  { to: '/app/home', label: 'Home' },
  { to: '/app/originals', label: 'Originals' },
  { to: '/app/shorts', label: 'Shorts' },
  { to: '/app/watchlist', label: 'My List' },
  { to: '/app/profile', label: 'Profile' },
  { to: '/', label: 'Website', external: true },
];

export default function AppSiteNav() {
  const { pathname } = useLocation();
  const { openSearch, openNotifications } = useAppUI();
  const { isDark, toggleTheme } = useTheme();
  const onHome = pathname === '/app/home';

  return (
    <header
      className={`sticky top-0 z-40 w-full pt-[env(safe-area-inset-top)]
        ${onHome
          ? 'bg-gradient-to-b from-black/75 via-black/40 to-transparent'
          : 'dark:bg-untold-dark/95 light:bg-white/95 backdrop-blur-xl border-b dark:border-untold-border/50 light:border-gray-200/80'
        }`}
    >
      <div className="flex items-center justify-between gap-2 h-12 px-3 sm:px-4">
        <Link to="/app/home" className="shrink-0" aria-label="UNTOLD Home">
          <Logo variant="nav" />
        </Link>

        <div className="flex items-center gap-0.5 shrink-0">
          <button
            type="button"
            onClick={openSearch}
            aria-label="Search"
            className="p-2 rounded-full dark:hover:bg-white/10 light:hover:bg-black/5"
          >
            <SearchIcon className="w-5 h-5 dark:text-white light:text-black" />
          </button>
          <button
            type="button"
            onClick={openNotifications}
            aria-label="Notifications"
            className="relative p-2 rounded-full dark:hover:bg-white/10 light:hover:bg-black/5"
          >
            <BellIcon className="w-5 h-5 dark:text-white light:text-black" />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-untold-gold" />
          </button>
          <button
            type="button"
            onClick={toggleTheme}
            aria-label="Toggle theme"
            className="p-2 rounded-full dark:hover:bg-white/10 light:hover:bg-black/5"
          >
            {isDark ? (
              <SunIcon className="w-4 h-4 text-untold-gold" />
            ) : (
              <MoonIcon className="w-4 h-4 text-untold-gold" />
            )}
          </button>
          <Link
            to="/membership"
            className="hidden sm:inline-flex ml-1 rounded-lg bg-untold-gold px-2.5 py-1.5 text-[10px] font-bold text-untold-dark whitespace-nowrap"
          >
            Premium
          </Link>
        </div>
      </div>

      <nav
        className="flex gap-2 overflow-x-auto scrollbar-hide px-3 sm:px-4 pb-2.5 snap-x snap-mandatory"
        aria-label="App sections"
      >
        {scrollLinks.map((link) =>
          link.external ? (
            <a
              key={link.to}
              href={link.to}
              className="snap-start shrink-0 rounded-full px-3 py-1.5 text-[11px] font-semibold whitespace-nowrap
                border border-untold-gold/40 text-untold-gold dark:bg-untold-gold/10 light:bg-untold-gold/15"
            >
              {link.label}
            </a>
          ) : (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) =>
                `snap-start shrink-0 rounded-full px-3 py-1.5 text-[11px] font-semibold whitespace-nowrap transition-colors
                ${isActive
                  ? 'bg-untold-gold text-untold-dark'
                  : 'dark:bg-white/8 light:bg-gray-100 dark:text-white/85 light:text-gray-700 border dark:border-white/10 light:border-gray-200'
                }`
              }
            >
              {link.label}
            </NavLink>
          )
        )}
      </nav>
    </header>
  );
}
