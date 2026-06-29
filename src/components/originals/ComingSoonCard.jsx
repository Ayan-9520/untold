import Badge from '../ui/Badge';
import { SPORT_CARD_THEMES } from '../../data/originalsCatalog';

export default function ComingSoonCard({ sport, teaser }) {
  const theme = SPORT_CARD_THEMES[sport] || SPORT_CARD_THEMES.Cricket;

  return (
    <article
      className={`relative w-full rounded-xl overflow-hidden border-l-4 ${theme.accent}
        dark:bg-untold-surface light:bg-white border dark:border-untold-border light:border-gray-200 opacity-90`}
    >
      <div className="relative aspect-video overflow-hidden">
        <img
          src={theme.image}
          alt=""
          className="h-full w-full object-cover scale-105 blur-[2px] brightness-50"
          loading="lazy"
        />
        <div className={`absolute inset-0 bg-gradient-to-t ${theme.gradient}`} />

        <div className="absolute inset-0 flex flex-col items-center justify-center p-6 text-center">
          <Badge variant="premium" size="lg" className="mb-3">
            Coming Soon
          </Badge>
          <p className="text-lg font-display font-bold text-white">{sport}</p>
          <p className="mt-2 text-sm text-white/75 max-w-[220px]">{teaser}</p>
        </div>

        <span className={`absolute top-3 left-3 px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase text-white ${theme.badge}`}>
          {sport}
        </span>
      </div>

      <div className="p-4 border-t dark:border-untold-border light:border-gray-100">
        <p className="text-sm dark:text-untold-muted light:text-gray-500 text-center">
          UNTOLD originals for {sport} are in production.
        </p>
      </div>
    </article>
  );
}
