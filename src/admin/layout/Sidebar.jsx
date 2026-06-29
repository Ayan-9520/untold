import Logo from '../../components/brand/Logo';
import { PRODUCTS } from '../../config/ecosystem';
import { STUDIO_NAV } from '../config/studioNav';
import { NavLink, Link } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { useAdminAuth } from '../context/AdminAuthContext';
import { useTheme } from '../../context/ThemeContext';
import { SunIcon, MoonIcon, MenuIcon, XIcon } from '../../components/icons';
import { LogOutIcon } from '../components/AdminIcons';

export default function Sidebar() {
  const [open, setOpen] = useState(false);
  const { logout, user } = useAdminAuth();
  const { isDark, toggleTheme } = useTheme();
  const studio = PRODUCTS.STUDIO;

  useEffect(() => {
    if (!open) return undefined;
    const prev = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = prev;
    };
  }, [open]);

  const NavContent = () => (
    <>
      <div className="px-5 py-6 border-b dark:border-white/10 light:border-gray-200">
        <Logo variant="nav" />
        <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-untold-gold mt-2">
          {studio.name}
        </p>
        <p className="text-[10px] uppercase tracking-[0.15em] dark:text-untold-muted light:text-gray-400 mt-1">
          {studio.tagline}
        </p>
      </div>

      <nav className="flex-1 px-3 py-4 overflow-y-auto space-y-5">
        {STUDIO_NAV.map((section) => (
          <div key={section.title}>
            <p className="px-3 mb-1.5 text-[10px] font-semibold uppercase tracking-wider dark:text-untold-muted/70 light:text-gray-400">
              {section.title}
            </p>
            <div className="space-y-0.5">
              {section.items.map(({ to, icon: Icon, label, end }) => (
                <NavLink
                  key={to}
                  to={to}
                  end={end}
                  onClick={() => setOpen(false)}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-all
                    ${isActive
                      ? 'bg-untold-gold/15 text-untold-gold'
                      : 'dark:text-untold-muted light:text-gray-500 hover:dark:text-untold-white hover:light:text-black hover:dark:bg-white/5 hover:light:bg-black/5'
                    }`
                  }
                >
                  <Icon className="w-4 h-4 shrink-0" />
                  {label}
                </NavLink>
              ))}
            </div>
          </div>
        ))}
      </nav>

      <div className="p-3 border-t dark:border-white/10 light:border-gray-200 space-y-1">
        <Link
          to="/"
          className="flex w-full items-center gap-3 px-3 py-2 rounded-lg text-xs
            dark:text-untold-muted light:text-gray-500 hover:dark:bg-white/5 hover:light:bg-black/5"
        >
          → {PRODUCTS.ORIGINALS.name}
        </Link>
        <button
          type="button"
          onClick={toggleTheme}
          className="flex w-full items-center gap-3 px-3 py-2.5 rounded-lg text-sm
            dark:text-untold-muted light:text-gray-500 hover:dark:bg-white/5 hover:light:bg-black/5 transition-colors"
        >
          {isDark ? <SunIcon className="w-5 h-5 text-untold-gold" /> : <MoonIcon className="w-5 h-5 text-untold-gold" />}
          {isDark ? 'Light Mode' : 'Dark Mode'}
        </button>
        <button
          type="button"
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
        type="button"
        onClick={() => setOpen(true)}
        className="lg:hidden fixed top-4 left-4 z-50 p-2 rounded-lg dark:bg-untold-surface light:bg-white shadow-lg"
        aria-label="Open menu"
        aria-expanded={open}
        aria-controls="studio-sidebar"
      >
        <MenuIcon className="w-5 h-5" />
      </button>

      {open && (
        <div className="lg:hidden fixed inset-0 z-40 bg-black/50" onClick={() => setOpen(false)} />
      )}

      <aside
        id="studio-sidebar"
        className={`fixed lg:static inset-y-0 left-0 z-50 w-64 flex flex-col
          dark:bg-untold-surface light:bg-white border-r dark:border-white/10 light:border-gray-200
          transform transition-transform lg:translate-x-0
          ${open ? 'translate-x-0' : '-translate-x-full'}`}
      >
        <button
          type="button"
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
