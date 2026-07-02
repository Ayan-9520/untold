import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import SEO from '../components/SEO';
import platformApi from '../api/platform';
import { FALLBACK_FAQ } from '../data/platformContent';

export default function HelpPage() {
  const { t } = useTranslation();
  const [items, setItems] = useState(FALLBACK_FAQ);
  const [openId, setOpenId] = useState(null);

  useEffect(() => {
    platformApi.listFaq().then(setItems).catch(() => setItems(FALLBACK_FAQ));
  }, []);

  const grouped = useMemo(() => {
    const map = {};
    items.forEach((item) => {
      if (!map[item.category]) map[item.category] = [];
      map[item.category].push(item);
    });
    return map;
  }, [items]);

  return (
    <>
      <SEO title={t('help.title')} description={t('help.subtitle')} path="/help" />
      <section className="pt-28 pb-16">
        <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8">
          <h1 className="font-display text-4xl font-bold dark:text-white light:text-black mb-2">{t('help.title')}</h1>
          <p className="text-sm dark:text-untold-muted light:text-gray-600 mb-8">
            {t('help.subtitle')} {t('help.stillNeed')}{' '}
            <Link to="/contact" className="text-untold-gold hover:underline">{t('help.contactUs')}</Link>
          </p>

          {Object.entries(grouped).map(([category, faqs]) => (
            <div key={category} className="mb-10">
              <h2 className="text-xs font-bold uppercase tracking-widest text-untold-gold mb-4">{category}</h2>
              <div className="space-y-2">
                {faqs.map((faq) => (
                  <div key={faq.id} className="rounded-xl border dark:border-untold-border light:border-gray-200 overflow-hidden">
                    <button
                      type="button"
                      className="w-full text-left px-4 py-3 font-medium dark:text-white light:text-black flex justify-between gap-4"
                      onClick={() => setOpenId(openId === faq.id ? null : faq.id)}
                      aria-expanded={openId === faq.id}
                    >
                      {faq.question}
                      <span className="text-untold-gold">{openId === faq.id ? '−' : '+'}</span>
                    </button>
                    {openId === faq.id && (
                      <p className="px-4 pb-4 text-sm dark:text-untold-muted light:text-gray-600">{faq.answer}</p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ))}

          <div className="mt-12 grid sm:grid-cols-2 gap-4">
            <Link to="/membership" className="profile-link-card p-5 block">
              <h3 className="font-semibold text-white">{t('help.membershipBilling')}</h3>
              <p className="text-sm text-untold-muted mt-1">{t('help.membershipDesc')}</p>
            </Link>
            <Link to="/app" className="profile-link-card p-5 block">
              <h3 className="font-semibold text-white">{t('help.mobileApp')}</h3>
              <p className="text-sm text-untold-muted mt-1">{t('help.mobileDesc')}</p>
            </Link>
          </div>
        </div>
      </section>
    </>
  );
}
