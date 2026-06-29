import Logo from '../../components/brand/Logo';
import {
  LayoutDashboardIcon,
  UsersIcon,
  FilmIcon,
  BarChartIcon,
  DollarSignIcon,
  BellIcon,
  LogOutIcon,
  MenuIcon,
  XIcon,
  GlobeIcon,
  CreditCardIcon,
  BookIcon,
} from '../components/AdminIcons';
import { NavLink } from 'react-router-dom';
import { useState } from 'react';
import { useAdminAuth } from '../context/AdminAuthContext';
import { useTheme } from '../../context/ThemeContext';
import { SunIcon, MoonIcon } from '../../components/icons';

const navItems = [
  { to: '/admin', icon: LayoutDashboardIcon, label: 'Dashboard', end: true },
  { to: '/admin/content', icon: FilmIcon, label: 'Content' },
  { to: '/admin/ai-localization', icon: GlobeIcon, label: 'AI Localization' },
  { to: '/admin/magazine', icon: BookIcon, label: 'E-Magazine' },
  { to: '/admin/users', icon: UsersIcon, label: 'Users' },
  { to: '/admin/membership', icon: CreditCardIcon, label: 'Membership' },
  { to: '/admin/analytics', icon: BarChartIcon, label: 'Analytics' },
  { to: '/admin/revenue', icon: DollarSignIcon, label: 'Revenue' },
  { to: '/admin/notifications', icon: BellIcon, label: 'Notifications' },
];

export default function Sidebar() {
  const [open, setOpen] = useState(false);
  const { logout, user } = useAdminAuth();
  const { isDark, toggleTheme } = useTheme();

  const NavContent = () => (
    <>
      <div className="px-5 py-6 border-b dark:border-white/10 light:border-gray-200">
        <Logo variant="nav" />
        <p className="text-[10px] uppercase tracking-[0.2em] dark:text-untold-muted light:text-gray-400 mt-2">
          Admin Console
        </p>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-1">
        {navItems.map(({ to, icon: Icon, label, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            onClick={() => setOpen(false)}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all
              ${isActive
                ? 'bg-untold-gold/15 text-untold-gold'
                : 'dark:text-untold-muted light:text-gray-500 hover:dark:text-untold-white hover:light:text-black hover:dark:bg-white/5 hover:light:bg-black/5'
              }`
            }
          >
            <Icon className="w-5 h-5 shrink-0" />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="p-3 border-t dark:border-white/10 light:border-gray-200 space-y-1">
        <button
          onClick={toggleTheme}
          className="flex w-full items-center gap-3 px-3 py-2.5 rounded-lg text-sm
            dark:text-untold-muted light:text-gray-500 hover:dark:bg-white/5 hover:light:bg-black/5 transition-colors"
        >
          {isDark ? <SunIcon className="w-5 h-5 text-untold-gold" /> : <MoonIcon className="w-5 h-5 text-untold-gold" />}
          {isDark ? 'Light Mode' : 'Dark Mode'}
        </button>
        <button
          onClick={logout}
          className="flex w-full items-center gap-3 px-3 py-2.5 rounded-lg text-sm
            text-red-400 hover:bg-red-500/10 transition-colors"
        >
          <LogOutIcon className="w-5 h-5" />
          Sign Out
        </button>
        {user && (
          <div className="px-3 pt-2">
            <p className="text-xs font-medium dark:text-untold-white light:text-black truncate">{user.full_name}</p>
            <p className="text-[10px] dark:text-untold-muted light:text-gray-400 truncate">{user.email}</p>
          </div>
        )}
      </div>
    </>
  );

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        className="lg:hidden fixed top-4 left-4 z-50 p-2 rounded-lg dark:bg-untold-surface light:bg-white shadow-lg"
        aria-label="Open menu"
      >
        <MenuIcon className="w-5 h-5" />
      </button>

      {open && (
        <div className="lg:hidden fixed inset-0 z-40 bg-black/50" onClick={() => setOpen(false)} />
      )}

      <aside
        className={`fixed lg:static inset-y-0 left-0 z-50 w-64 flex flex-col
          dark:bg-untold-surface light:bg-white border-r dark:border-white/10 light:border-gray-200
          transform transition-transform lg:translate-x-0
          ${open ? 'translate-x-0' : '-translate-x-full'}`}
      >
        <button
          onClick={() => setOpen(false)}
          className="lg:hidden absolute top-4 right-4 p-1"
          aria-label="Close menu"
        >
          <XIcon className="w-5 h-5" />
        </button>
        <NavContent />
      </aside>
    </>
  );
}
