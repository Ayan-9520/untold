import { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocale } from '../../context/LocaleContext';

export default function RegionSelector({ className = '', inMenu = false }) {
  const { t } = useTranslation();
  const { region, regions, setRegion } = useLocale();
  const [open, setOpen] = useState(false);
  const ref = useRef(null);

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
        aria-label={t('selectors.region')}
        aria-expanded={open}
        className={inMenu ? 'menu-selector-btn' : 'site-selector-btn'}
      >
        <span aria-hidden>🌍</span>
        <span className={inMenu ? '' : 'hidden sm:inline max-w-[5rem] truncate'}>
          {region.flag} {region.label}
        </span>
      </button>

      {open && (
        <div className={`menu-dropdown ${inMenu ? 'menu-dropdown--in-menu' : ''}`}>
          <p className="menu-dropdown-label">{t('selectors.region')}</p>
          {regions.map((r) => (
            <button
              key={r.id}
              type="button"
              onClick={() => {
                setRegion(r.id);
                setOpen(false);
              }}
              className={`menu-dropdown-item ${region.id === r.id ? 'menu-dropdown-item--active' : ''}`}
            >
              <span>{r.flag}</span>
              <span className="flex-1 text-left">{r.label}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
