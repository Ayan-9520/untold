import { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { INDIAN_LANGUAGES, INTERNATIONAL_LANGUAGES } from '../../data/regionalConfig';

export default function LanguageSelector({ className = '', inMenu = false }) {
  const { i18n, t } = useTranslation();
  const [open, setOpen] = useState(false);
  const ref = useRef(null);

  const allLanguages = [...INDIAN_LANGUAGES, ...INTERNATIONAL_LANGUAGES];
  const current = allLanguages.find((l) => l.code === i18n.language) || allLanguages[0];

  useEffect(() => {
    const onClick = (e) => {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false);
    };
    document.addEventListener('mousedown', onClick);
    return () => document.removeEventListener('mousedown', onClick);
  }, []);

  const selectLanguage = (code) => {
    i18n.changeLanguage(code);
    setOpen(false);
  };

  const renderGroup = (labelKey, languages) => (
    <>
      <p className="menu-dropdown-label menu-dropdown-label--group">{t(labelKey)}</p>
      {languages.map((lang) => (
        <button
          key={lang.code}
          type="button"
          onClick={() => selectLanguage(lang.code)}
          className={`menu-dropdown-item ${i18n.language === lang.code ? 'menu-dropdown-item--active' : ''}`}
        >
          <span>{lang.native}</span>
          <span className="menu-dropdown-sub">({lang.label})</span>
        </button>
      ))}
    </>
  );

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
        <span className={inMenu ? '' : 'hidden sm:inline max-w-[5rem] truncate'}>
          {current.native}
        </span>
      </button>

      {open && (
        <div className={`menu-dropdown menu-dropdown--languages ${inMenu ? 'menu-dropdown--in-menu' : ''}`}>
          <p className="menu-dropdown-label">{t('selectors.language')}</p>
          {renderGroup('selectors.indiaLanguages', INDIAN_LANGUAGES)}
          <div className="menu-dropdown-divider" role="separator" />
          {renderGroup('selectors.international', INTERNATIONAL_LANGUAGES)}
        </div>
      )}
    </div>
  );
}
