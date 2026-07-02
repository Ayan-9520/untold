import { useState, useEffect, useRef } from 'react';
import { Link, NavLink } from 'react-router-dom';
import { createPortal } from 'react-dom';
import { useTranslation } from 'react-i18next';
import { useWebAuth } from '../../context/WebAuthContext';
import { useTheme } from '../../context/ThemeContext';
import Logo from '../brand/Logo';
import SearchBar from '../ui/SearchBar';
import ThemeToggle from '../ui/ThemeToggle';
import RegionSelector from '../ui/RegionSelector';
import LanguageSelector from '../ui/LanguageSelector';
import LanguageQuickBar from '../ui/LanguageQuickBar';
import MenuSearchField from '../ui/MenuSearchField';
import { CloseIcon, MenuIcon } from '../icons';
import { PRIMARY_NAV, MORE_NAV } from '../../data/siteNav';

const primaryNav = PRIMARY_NAV;
const moreNav = MORE_NAV;

function MobileMenu({ open, onClose, t, isAuthenticated, user, logout }) {
  const { isDark } = useTheme();

  useEffect(() => {
    if (!open) return;
    const prev = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = prev;
    };
  }, [open]);

  useEffect(() => {
    if (!open) return;
    const onKey = (e) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [open, onClose]);

  if (!open) return null;

  return createPortal(
    <div className="site-mobile-menu" role="dialog" aria-modal="true" aria-label="Menu">
      <button type="button" className="site-mobile-menu-backdrop" onClick={onClose} aria-label="Close menu" />
      <div className={`site-mobile-menu-panel ${isDark ? '' : 'site-mobile-menu-panel--light'}`}>
        <div className="site-mobile-menu-header">
          <Link to="/" onClick={onClose} className="site-header-logo">
            <Logo variant="stacked" />
          </Link>
          <button type="button" className="site-mobile-menu-close" onClick={onClose} aria-label="Close">
            <CloseIcon className="w-6 h-6" />
          </button>
        </div>

        <div className="site-mobile-menu-body">
          <div className="site-mobile-menu-settings">
            <p className="site-mobile-menu-settings-title">Appearance</p>
            <ThemeToggle variant="segment" className="w-full" />

            <p className="site-mobile-menu-settings-title">Preferences</p>
            <div className="site-mobile-menu-prefs">
              <LanguageQuickBar />
              <RegionSelector inMenu />
              <LanguageSelector inMenu />
            </div>

            <MenuSearchField onNavigate={onClose} />
          </div>

          <p className="site-mobile-menu-label">{t('nav.browse', 'Browse')}</p>
          {primaryNav.map(({ to, key, live }) => (
            <NavLink
              key={to}
              to={to}
              onClick={onClose}
              className={({ isActive }) =>
                `site-mobile-menu-link${isActive ? ' site-mobile-menu-link--active' : ''}${live ? ' site-mobile-menu-link--live' : ''}`
              }
            >
              {t(`nav.${key}`)}
              {live && <span className="site-header-live-dot" aria-hidden="true" />}
            </NavLink>
          ))}

          <Link to="/membership" onClick={onClose} className="site-mobile-menu-cta">
            {t('nav.membership')}
          </Link>

          <p className="site-mobile-menu-label">{t('nav.more', 'More')}</p>
          {moreNav.map(({ to, key }) => (
            <NavLink
              key={to}
              to={to}
              onClick={onClose}
              className={({ isActive }) =>
                `site-mobile-menu-link site-mobile-menu-link--muted${isActive ? ' site-mobile-menu-link--active' : ''}`
              }
            >
              {t(`nav.${key}`)}
            </NavLink>
          ))}

          {isAuthenticated ? (
            <>
              <Link to="/profile" onClick={onClose} className="site-mobile-menu-link site-mobile-menu-link--gold">
                {user?.name || t('nav.profile')}
              </Link>
              <button type="button" onClick={() => { logout(); onClose(); }} className="site-mobile-menu-link site-mobile-menu-link--muted w-full text-left">
                {t('nav.logout')}
              </button>
            </>
          ) : (
            <Link to="/login" onClick={onClose} className="site-mobile-menu-link site-mobile-menu-link--gold">
              {t('nav.login')}
            </Link>
          )}
        </div>
      </div>
    </div>,
    document.body
  );
}

export default function Navbar() {
  const { t } = useTranslation();
  const { isAuthenticated, user, logout } = useWebAuth();
  const [menuOpen, setMenuOpen] = useState(false);
  const [moreOpen, setMoreOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const moreRef = useRef(null);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 24);
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  useEffect(() => {
    if (!menuOpen) return;
    const onResize = () => {
      if (window.innerWidth >= 768) setMenuOpen(false);
    };
    window.addEventListener('resize', onResize);
    return () => window.removeEventListener('resize', onResize);
  }, [menuOpen]);

  useEffect(() => {
    if (!moreOpen) return;
    const onClick = (e) => {
      if (moreRef.current && !moreRef.current.contains(e.target)) setMoreOpen(false);
    };
    document.addEventListener('click', onClick);
    return () => document.removeEventListener('click', onClick);
  }, [moreOpen]);

  const headerClass = scrolled ? 'site-header site-header--solid' : 'site-header site-header--transparent';

  return (
    <>
      <header className={headerClass}>
        <div className="site-header-inner">
          <Link to="/" className="site-header-logo site-header-brand" aria-label="UNTOLD Originals — Home">
            <Logo variant="stacked" />
          </Link>

          <nav className="site-header-nav hidden md:flex" aria-label="Main">
            {primaryNav.map(({ to, key, live }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) =>
                  `site-header-link${isActive ? ' site-header-link--active' : ''}${live ? ' site-header-link--live' : ''}`
                }
              >
                {t(`nav.${key}`)}
                {live && <span className="site-header-live-dot" aria-hidden="true" />}
              </NavLink>
            ))}
            <div className="relative" ref={moreRef}>
              <button
                type="button"
                className={`site-header-link site-header-link--more${moreOpen ? ' site-header-link--active' : ''}`}
                onClick={() => setMoreOpen((o) => !o)}
                aria-expanded={moreOpen}
              >
                {t('nav.more', 'More')}
              </button>
              {moreOpen && (
                <div className="site-header-more-menu">
                  {moreNav.map(({ to, key }) => (
                    <NavLink
                      key={to}
                      to={to}
                      onClick={() => setMoreOpen(false)}
                      className={({ isActive }) =>
                        `site-header-more-link${isActive ? ' site-header-more-link--active' : ''}`
                      }
                    >
                      {t(`nav.${key}`)}
                    </NavLink>
                  ))}
                </div>
              )}
            </div>
          </nav>

          <div className="site-header-actions">
            <div className="hidden md:flex items-center gap-0.5">
              <SearchBar />
              <RegionSelector />
              <LanguageSelector />
              <ThemeToggle />
              <Link to="/membership" className="site-header-membership">
                {t('nav.membership')}
              </Link>
            </div>

            <div className="flex md:hidden items-center gap-0.5">
              <ThemeToggle />
              <button
                type="button"
                className="site-header-menu-btn"
                onClick={() => setMenuOpen((o) => !o)}
                aria-expanded={menuOpen}
                aria-label={menuOpen ? 'Close menu' : 'Open menu'}
              >
                {menuOpen ? <CloseIcon className="w-6 h-6" /> : <MenuIcon className="w-6 h-6" />}
              </button>
            </div>
          </div>
        </div>
        <LanguageQuickBar />
      </header>

      <MobileMenu
        open={menuOpen}
        onClose={() => setMenuOpen(false)}
        t={t}
        isAuthenticated={isAuthenticated}
        user={user}
        logout={logout}
      />
    </>
  );
}
