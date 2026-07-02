import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import SEO from '../components/SEO';

export default function AppDownloadPage() {
  const { t } = useTranslation();

  const stores = [
    { id: 'ios', label: t('app.downloadIos'), href: '#', soon: true },
    { id: 'android', label: t('app.downloadAndroid'), href: '#', soon: true },
  ];

  return (
    <>
      <SEO title={t('profile.mobileApp')} description={t('app.subtitle')} path="/app" />
      <section className="pt-28 pb-16">
        <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <p className="text-xs font-bold uppercase tracking-[0.35em] text-untold-gold mb-3">UNTOLD Mobile</p>
              <h1 className="font-display text-4xl sm:text-5xl font-bold text-white mb-4">{t('app.title')}</h1>
              <p className="text-untold-muted mb-8">{t('app.subtitle')}</p>
              <div className="flex flex-wrap gap-3">
                {stores.map((store) => (
                  <a
                    key={store.id}
                    href={store.href}
                    className={`px-5 py-3 rounded-xl border border-untold-border bg-untold-surface text-left min-w-[200px] ${store.soon ? 'opacity-70 cursor-default' : 'hover:border-untold-gold'}`}
                    onClick={store.soon ? (e) => e.preventDefault() : undefined}
                  >
                    <p className="text-sm font-semibold text-white">{store.label}</p>
                    <p className="text-xs text-untold-muted">{store.soon ? t('app.comingSoon') : store.id}</p>
                  </a>
                ))}
              </div>
              <p className="mt-6 text-sm text-untold-muted">{t('app.mobileWeb')}</p>
            </div>
            <div className="rounded-2xl border border-untold-border bg-gradient-to-br from-untold-surface to-black p-8 aspect-[4/5] max-w-sm mx-auto flex items-center justify-center">
              <div className="text-center">
                <div className="w-24 h-24 mx-auto rounded-2xl bg-untold-gold/20 border border-untold-gold/40 flex items-center justify-center text-4xl mb-4">▶</div>
                <p className="font-display text-xl font-bold text-white">UNTOLD</p>
                <p className="text-xs text-untold-muted mt-1">ORIGINALS</p>
              </div>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
