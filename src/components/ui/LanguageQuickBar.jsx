import { useTranslation } from 'react-i18next';
import { FAMOUS_INDIAN_LANGUAGES, isIndianLanguage, currencyForLanguage } from '../../data/regionalConfig';

/**
 * One-tap language switcher for popular Indian languages.
 * Selecting any language translates the UI and switches pricing to ₹ INR.
 */
export default function LanguageQuickBar() {
  const { i18n, t } = useTranslation();
  const currency = currencyForLanguage(i18n.language);
  const showInr = isIndianLanguage(i18n.language);

  return (
    <div className="language-quick-bar" role="navigation" aria-label={t('selectors.language')}>
      <div className="language-quick-bar-inner">
        <span className="language-quick-bar-label">{t('selectors.language')}:</span>
        <div className="language-quick-bar-pills">
          {FAMOUS_INDIAN_LANGUAGES.map((lang) => (
            <button
              key={lang.code}
              type="button"
              className={`language-quick-pill${i18n.language === lang.code ? ' language-quick-pill--active' : ''}`}
              onClick={() => i18n.changeLanguage(lang.code)}
              aria-pressed={i18n.language === lang.code}
            >
              {lang.native}
            </button>
          ))}
        </div>
        {showInr && (
          <span className="language-quick-bar-currency" title={t('selectors.currency')}>
            ₹ INR
          </span>
        )}
      </div>
    </div>
  );
}
