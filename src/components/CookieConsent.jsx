import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

const KEY = 'untold-cookie-consent';

export default function CookieConsent() {
  const { t } = useTranslation();
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    try {
      if (!localStorage.getItem(KEY)) setVisible(true);
    } catch {
      setVisible(true);
    }
  }, []);

  const accept = () => {
    try { localStorage.setItem(KEY, 'accepted'); } catch { /* ignore */ }
    setVisible(false);
  };

  if (!visible) return null;

  return (
    <div className="cookie-consent" role="dialog" aria-label={t('cookies.accept')}>
      <p className="cookie-consent-text">
        {t('cookies.message')}{' '}
        <a href="/legal/privacy" className="text-untold-gold hover:underline">{t('footer.privacy')}</a>
      </p>
      <button type="button" className="cookie-consent-btn" onClick={accept}>{t('cookies.accept')}</button>
    </div>
  );
}
