import { useTranslation } from 'react-i18next';
import SectionReveal from '../ui/SectionReveal';

const FEATURES = [
  { key: 'aiRecommendations', icon: '✦' },
  { key: 'personalizedFeed', icon: '◎' },
  { key: 'liveNotifications', icon: '●' },
  { key: 'multiLanguage', icon: '◈' },
  { key: 'multiCurrency', icon: '◇' },
];

export default function PlatformFeatures() {
  const { t } = useTranslation();

  return (
    <SectionReveal className="py-8 border-t dark:border-untold-border/50 light:border-gray-200">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <p className="text-center text-[10px] font-bold uppercase tracking-[0.35em] text-untold-gold mb-4">
          {t('platform.comingSoon', 'Platform Intelligence')}
        </p>
        <div className="flex flex-wrap justify-center gap-3 sm:gap-4">
          {FEATURES.map(({ key, icon }) => (
            <div
              key={key}
              className="glass-card flex items-center gap-2 rounded-full px-4 py-2 text-xs font-medium
                dark:text-untold-white/80 light:text-gray-700"
            >
              <span className="text-untold-gold">{icon}</span>
              {t(`platform.${key}`)}
              <span className="text-[9px] uppercase tracking-wider text-untold-gold/70 ml-1">
                {t('platform.soon', 'Soon')}
              </span>
            </div>
          ))}
        </div>
      </div>
    </SectionReveal>
  );
}
