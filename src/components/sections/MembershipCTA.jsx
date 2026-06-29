import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import Button from '../ui/Button';
import { PlayIcon } from '../icons';
import { useLocale } from '../../context/LocaleContext';
import SectionReveal from '../ui/SectionReveal';

export default function MembershipCTA() {
  const { t } = useTranslation();
  const { formatPrice, pricing } = useLocale();

  return (
    <SectionReveal
      className="relative py-16 sm:py-24 overflow-hidden"
      aria-labelledby="membership-cta"
    >
      <div className="absolute inset-0 dark:bg-gradient-to-br dark:from-untold-gold/10 dark:via-untold-surface dark:to-untold-dark light:bg-gradient-to-br light:from-untold-gold/15 light:via-white light:to-gray-50" />
      <div className="absolute inset-0 cinematic-noise opacity-30 pointer-events-none" />

      <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="rounded-2xl border dark:border-untold-gold/30 light:border-untold-gold/40 p-8 sm:p-12 lg:p-16
          dark:bg-untold-surface/90 light:bg-white/95 backdrop-blur-md shadow-2xl gold-glow">
          <div className="grid lg:grid-cols-2 gap-10 lg:gap-14 items-center">
            <div>
              <p className="text-xs font-bold uppercase tracking-[0.35em] text-untold-gold mb-4">
                {t('membership.ctaEyebrow', 'UNTOLD Premium')}
              </p>
              <h2
                id="membership-cta"
                className="font-display text-3xl sm:text-4xl lg:text-5xl font-bold dark:text-untold-white light:text-black leading-tight"
              >
                {t('membership.ctaTitle', 'Unlock Premium UNTOLD')}
              </h2>
              <p className="mt-4 text-base sm:text-lg dark:text-untold-muted light:text-gray-600 max-w-lg">
                {t(
                  'membership.ctaSubtitle',
                  'Get exclusive documentaries, premium live coverage, and quarterly sports magazine access.'
                )}
              </p>

              <div className="mt-8 flex flex-wrap gap-3">
                <Link to="/membership">
                  <Button size="lg" icon={<PlayIcon className="w-4 h-4" />} className="gold-glow-sm">
                    {t('membership.subscribeNow', 'Subscribe Now')}
                  </Button>
                </Link>
                <Link to="/membership">
                  <Button variant="outline" size="lg">
                    {t('membership.comparePlans', 'Compare Plans')}
                  </Button>
                </Link>
              </div>
            </div>

            <div className="grid sm:grid-cols-3 gap-4">
              {[
                { id: 'free', name: t('membership.free'), price: formatPrice(pricing.free), tag: t('membership.adsEnabled', 'Ads') },
                { id: 'premium', name: t('membership.premium'), price: formatPrice(pricing.premium), tag: t('membership.adFree', 'Ad-free'), highlight: true },
                { id: 'vip', name: t('membership.vip'), price: formatPrice(pricing.vip), tag: t('membership.liveSports', 'Live sports') },
              ].map((plan) => (
                <div
                  key={plan.id}
                  className={`rounded-xl p-5 border text-center card-premium
                    ${plan.highlight
                      ? 'border-untold-gold dark:bg-untold-gold/10 light:bg-untold-gold/5 scale-[1.03] gold-glow-sm'
                      : 'dark:border-untold-border light:border-gray-200 dark:bg-untold-dark/50 light:bg-gray-50'
                    }`}
                >
                  <p className="text-xs font-semibold uppercase tracking-wider text-untold-gold">{plan.name}</p>
                  <p className="mt-2 text-2xl font-bold dark:text-untold-white light:text-black">{plan.price}</p>
                  <p className="mt-1 text-[10px] uppercase tracking-wider dark:text-untold-muted light:text-gray-500">{plan.tag}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </SectionReveal>
  );
}
