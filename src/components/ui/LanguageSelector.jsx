import { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { LANGUAGES } from '../../data/regionalConfig';

export default function LanguageSelector({ className = '', inMenu = false }) {
  const { i18n, t } = useTranslation();
  const [open, setOpen] = useState(false);
  const ref = useRef(null);

  const current = LANGUAGES.find((l) => l.code === i18n.language) || LANGUAGES[0];

  useEffect(() => {
    const onClick = (e) => {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false);
    };
    document.addEventListener('mousedown', onClick);
    return () => document.removeEventListener('mousedown', onClick);
  }, []);

  return (
    <div ref={ref} className={`relative ${inMenu ? 'menu-selector' : ''} ${className}`}>
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        aria-label={t('selectors.language')}
        aria-expanded={open}
        className={inMenu ? 'menu-selector-btn' : 'site-selector-btn'}
      >
        <span aria-hidden>🌐</span>
        <span className={inMenu ? '' : 'hidden sm:inline max-w-[4rem] truncate'}>
          {current.native}
        </span>
      </button>

      {open && (
        <div className={`menu-dropdown ${inMenu ? 'menu-dropdown--in-menu' : ''}`}>
          <p className="menu-dropdown-label">{t('selectors.language')}</p>
          {LANGUAGES.map((lang) => (
            <button
              key={lang.code}
              type="button"
              onClick={() => {
                i18n.changeLanguage(lang.code);
                setOpen(false);
              }}
              className={`menu-dropdown-item ${i18n.language === lang.code ? 'menu-dropdown-item--active' : ''}`}
            >
              <span>{lang.native}</span>
              <span className="menu-dropdown-sub">({lang.label})</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
