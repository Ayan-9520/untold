import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import SEO from '../SEO';
import VideoCard, { VideoCardSkeleton } from '../ui/VideoCard';
import ContentFilterBar from '../ui/ContentFilterBar';
import { contentApi } from '../../api/content';
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

const CATEGORY_META = {
  legends: { tagline: 'Icons', description: 'Athlete legacy storytelling across every sport.' },
  rivalries: { tagline: 'Feuds', description: 'The rivalries that defined eras.' },
  stories: { tagline: 'Inspiration', description: 'Emotional comebacks and historic wins.' },
  secrets: { tagline: 'Untold Truths', description: 'Hidden stories the world never saw.' },
};

export default function CategoryPage({ category, title, tagline, description }) {
  const [activeSport, setActiveSport] = useState('All');
  const [allItems, setAllItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const meta = CATEGORY_META[category] || {};
  const cardVariant = CARD_VARIANTS[category] || 'default';

  useEffect(() => {
    setLoading(true);
    contentApi.getCatalogByCategory(category)
      .then(({ data }) => setAllItems(data))
      .catch(() => setAllItems([]))
      .finally(() => setLoading(false));
  }, [category]);

  const sports = useMemo(() => getSportsFromItems(allItems, 'category'), [allItems]);
  const sportCounts = useMemo(() => buildSportCounts(allItems, 'category'), [allItems]);
  const filtered = useMemo(
    () => filterBySport(allItems, activeSport, 'category'),
    [allItems, activeSport]
  );

  return (
    <>
      <SEO title={title} description={description || meta.description} path={`/${category}`} />

      <section className="pt-28 pb-12 sm:pt-36 sm:pb-16">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-6 max-w-2xl mx-auto">
            <p className="dark:text-untold-gold light:text-untold-gold-dark text-xs font-semibold tracking-[0.3em] uppercase mb-2">
              {tagline || meta.tagline}
            </p>
            <h1 className="font-display text-3xl sm:text-4xl font-bold dark:text-untold-white light:text-black">
              {title}
            </h1>
            <p className="mt-3 text-sm sm:text-base dark:text-untold-muted light:text-gray-600">
              {description || meta.description}
            </p>
          </div>

          {!loading && allItems.length > 0 && (
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
          )}

          <div className={CONTENT_GRID_CLASS}>
            {loading
              ? [...Array(8)].map((_, i) => <VideoCardSkeleton key={i} fluid />)
              : filtered.length === 0
                ? (
                  <p className="col-span-full text-center py-12 text-sm dark:text-untold-muted light:text-gray-500">
                    No titles for this category yet.
                  </p>
                )
                : filtered.map((item) => (
                  <Link key={item.id} to={`/video/${item.id}`} className="block min-w-0">
                    <VideoCard
                      title={item.title}
                      image={item.image}
                      category={item.category || item.sport}
                      format={item.format || item.videoType}
                      duration={item.duration}
                      year={item.year}
                      description={item.description}
                      showDescription
                      videoId={item.id}
                      trailerUrl={item.videoUrl}
                      variant={cardVariant}
                      fluid
                    />
                  </Link>
                ))}
          </div>
        </div>
      </section>
    </>
  );
}
