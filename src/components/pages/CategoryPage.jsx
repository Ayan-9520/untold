import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import SEO from '../SEO';
import VideoCard from '../ui/VideoCard';
import ContentFilterBar from '../ui/ContentFilterBar';
import { getByCategory, CATEGORIES } from '../../data/videoCatalog';
import {
  buildSportCounts,
  filterBySport,
  getSportsFromItems,
  toSportOptions,
} from '../../utils/contentFilters';
import { CONTENT_GRID_CLASS } from '../../constants/contentLayout';

const CARD_VARIANTS = {
  legends: 'legend',
  rivalries: 'rivalry',
};

export default function CategoryPage({ category, title, tagline, description }) {
  const [activeSport, setActiveSport] = useState('All');
  const allItems = getByCategory(category);
  const meta = CATEGORIES.find((c) => c.slug === category);
  const cardVariant = CARD_VARIANTS[category] || 'default';

  const sports = useMemo(() => getSportsFromItems(allItems), [allItems]);
  const sportCounts = useMemo(() => buildSportCounts(allItems), [allItems]);
  const filtered = useMemo(
    () => filterBySport(allItems, activeSport),
    [allItems, activeSport]
  );

  return (
    <>
      <SEO title={title} description={description} path={`/${category}`} />

      <section className="pt-28 pb-12 sm:pt-36 sm:pb-16">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-6 max-w-2xl mx-auto">
            <p className="dark:text-untold-gold light:text-untold-gold-dark text-xs font-semibold tracking-[0.3em] uppercase mb-2">
              {tagline}
            </p>
            <h1 className="font-display text-3xl sm:text-4xl font-bold dark:text-untold-white light:text-black">
              {title}
            </h1>
            <p className="mt-3 text-sm sm:text-base dark:text-untold-muted light:text-gray-600">
              {description || meta?.description}
            </p>
          </div>

          <ContentFilterBar
            primary={{
              label: 'Sport',
              options: toSportOptions(sports, sportCounts),
              active: activeSport,
              onChange: setActiveSport,
            }}
            resultCount={filtered.length}
            resultLabel="titles"
            onClear={() => setActiveSport('All')}
          />

          <div className={CONTENT_GRID_CLASS}>
            {filtered.length === 0 ? (
              <p className="col-span-full text-center py-12 text-sm dark:text-untold-muted light:text-gray-500">
                No titles for this sport yet.
              </p>
            ) : (
              filtered.map((item) => (
                <Link key={item.id} to={`/video/${item.id}`} className="block min-w-0">
                  <VideoCard
                    title={item.title}
                    image={item.image}
                    category={item.sport}
                    format={item.format}
                    duration={item.duration}
                    year={item.year}
                    description={item.description}
                    showDescription
                    videoId={item.id}
                    trailerUrl={item.trailerUrl}
                    variant={cardVariant}
                    fluid
                  />
                </Link>
              ))
            )}
          </div>
        </div>
      </section>
    </>
  );
}
