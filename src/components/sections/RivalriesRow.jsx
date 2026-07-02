import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { contentApi } from '../../api/content';
import SectionHeader from '../ui/SectionHeader';
import ContentRow from '../ui/ContentRow';
import SectionReveal from '../ui/SectionReveal';
import Badge from '../ui/Badge';

export default function RivalriesRow({ limit = 6 }) {
  const [items, setItems] = useState([]);

  useEffect(() => {
    contentApi.getCatalogByCategory('rivalries')
      .then(({ data }) => setItems(data.slice(0, limit)))
      .catch(() => setItems([]));
  }, [limit]);

  if (items.length === 0) return null;

  return (
    <SectionReveal className="py-12 sm:py-16 section-cinematic" aria-labelledby="rivalries-row">
      <SectionHeader
        title="Rivalries"
        subtitle="Legendary battles — pick a side"
        viewAllLink="/rivalries"
      />
      <ContentRow>
        {items.map((item) => (
          <Link
            key={item.id}
            to={`/video/${item.id}`}
            className="group shrink-0 w-[280px] sm:w-[320px] card-premium"
          >
            <article className="relative rounded-xl overflow-hidden border dark:border-untold-border light:border-gray-200 dark:bg-untold-surface light:bg-white">
              <div className="relative aspect-[16/10] overflow-hidden">
                <img
                  src={item.image}
                  alt=""
                  loading="lazy"
                  className="h-full w-full object-cover transition-transform duration-700 group-hover:scale-110"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black via-black/50 to-transparent" />
                <Badge variant="gold" size="sm" className="absolute top-3 left-3">
                  {item.category || item.sport}
                </Badge>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="font-display text-3xl sm:text-4xl font-bold text-untold-gold drop-shadow-lg gold-glow-text">
                    VS
                  </span>
                </div>
              </div>
              <div className="p-4">
                <h3 className="font-display text-lg font-bold dark:text-untold-white light:text-black group-hover:text-untold-gold transition-colors line-clamp-2">
                  {item.title}
                </h3>
                {item.description && (
                  <p className="mt-1 text-xs dark:text-untold-muted light:text-gray-500 line-clamp-2">
                    {item.description}
                  </p>
                )}
              </div>
            </article>
          </Link>
        ))}
      </ContentRow>
    </SectionReveal>
  );
}
