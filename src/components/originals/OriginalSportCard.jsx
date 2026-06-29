import { useState } from 'react';
import { Link } from 'react-router-dom';
import Badge from '../ui/Badge';
import { SPORT_CARD_THEMES } from '../../data/originalsCatalog';

export default function OriginalSportCard({ item }) {
  const sport = item.sport || item.category || 'Cricket';
  const theme = SPORT_CARD_THEMES[sport] || SPORT_CARD_THEMES.Cricket;
  const fallbackImage = theme.image;
  const [imgSrc, setImgSrc] = useState(item.image || fallbackImage);

  return (
    <Link to={`/video/${item.id}`} className="block w-full group card-premium">
      <article
        className={`w-full rounded-xl overflow-hidden border-l-4 ${theme.accent}
          dark:bg-untold-surface light:bg-white border dark:border-untold-border light:border-gray-200`}
      >
        <div className="relative aspect-video overflow-hidden">
          <img
            src={imgSrc}
            alt={item.title}
            loading="lazy"
            onError={() => setImgSrc(fallbackImage)}
            className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
          />
          <div className={`absolute inset-0 bg-gradient-to-t ${theme.gradient}`} />

          <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-untold-gold text-untold-dark play-glow transform scale-90 group-hover:scale-100 transition-transform">
              <svg className="w-5 h-5 ml-0.5" viewBox="0 0 24 24" fill="currentColor">
                <path d="M8 5v14l11-7z" />
              </svg>
            </div>
          </div>

          {item.duration && (
            <span className="absolute bottom-2 right-2 px-2 py-0.5 rounded text-xs font-medium bg-black/70 text-white backdrop-blur-sm">
              {item.duration}
            </span>
          )}
        </div>

        <div className="p-4">
          <h3 className="font-display text-base sm:text-lg font-bold leading-snug line-clamp-2 dark:text-untold-white light:text-black group-hover:text-untold-gold transition-colors">
            {item.title}
          </h3>
          {item.description && (
            <p className="mt-2 text-sm dark:text-untold-muted light:text-gray-600 line-clamp-2">
              {item.description}
            </p>
          )}
          <div className="mt-3 pt-3 border-t dark:border-untold-border/60 light:border-gray-100 flex flex-wrap items-center gap-2">
            <Badge variant="gold" size="sm">{sport}</Badge>
            {item.format && <Badge variant="muted" size="sm">{item.format}</Badge>}
            {item.year && <Badge variant="outline" size="sm">{item.year}</Badge>}
            {item.rating && <Badge variant="outline" size="sm">{item.rating}</Badge>}
          </div>
        </div>
      </article>
    </Link>
  );
}
