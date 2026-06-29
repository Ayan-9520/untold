import { SearchIcon, BellIcon } from '../../components/icons';
import Logo from '../../components/brand/Logo';
import { useAppUI } from '../context/AppUIContext';
import { useTheme } from '../../context/ThemeContext';
import { SunIcon, MoonIcon } from '../../components/icons';

export default function TopBar({ title, showLogo = false, transparent = false }) {
  const { openSearch, openNotifications } = useAppUI();
  const { isDark, toggleTheme } = useTheme();

  return (
    <header
      className={`sticky top-0 z-30 flex items-center justify-between h-12 px-4 pt-[env(safe-area-inset-top)]
        ${transparent
          ? 'bg-transparent'
          : 'dark:bg-untold-dark/90 light:bg-white/90 backdrop-blur-xl border-b dark:border-untold-border/40 light:border-gray-100'
        }`}
    >
      {showLogo ? (
        <Logo variant="nav" />
      ) : (
        <h1 className="text-base font-semibold dark:text-untold-white light:text-black truncate">
          {title}
        </h1>
      )}

      <div className="flex items-center gap-1">
        <button
          onClick={openSearch}
          aria-label="Search"
          className="p-2 rounded-full dark:hover:bg-white/10 light:hover:bg-black/5 transition-colors"
        >
          <SearchIcon className="w-5 h-5 dark:text-untold-white light:text-black" />
        </button>
        <button
          onClick={openNotifications}
          aria-label="Notifications"
          className="relative p-2 rounded-full dark:hover:bg-white/10 light:hover:bg-black/5 transition-colors"
        >
          <BellIcon className="w-5 h-5 dark:text-untold-white light:text-black" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-untold-gold" />
        </button>
        <button
          onClick={toggleTheme}
          aria-label="Toggle theme"
          className="p-2 rounded-full dark:hover:bg-white/10 light:hover:bg-black/5 transition-colors"
        >
          {isDark ? (
            <SunIcon className="w-4 h-4 text-untold-gold" />
          ) : (
            <MoonIcon className="w-4 h-4 text-untold-gold" />
          )}
        </button>
      </div>
    </header>
  );
}
