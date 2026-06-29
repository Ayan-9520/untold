import { useMemo, useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import SEO from '../components/SEO';
import VideoCard from '../components/ui/VideoCard';
import ShortsCard from '../components/ui/ShortsCard';
import ContentRow from '../components/ui/ContentRow';
import SectionHeader from '../components/ui/SectionHeader';
import ContentFilterBar from '../components/ui/ContentFilterBar';
import { SearchIcon } from '../components/icons';
import { EXPLORE_SPORTS, EXPLORE_CATEGORIES, SORT_OPTIONS } from '../data/siteConfig';
import { videoCatalog } from '../data/videoCatalog';
import {
  exploreSearch,
  filterVideosBySport,
  sortVideos,
  getRecommendedVideos,
  getTrendingVideos,
} from '../utils/exploreSearch';
import { CONTENT_GRID_CLASS } from '../constants/contentLayout';

function CategoryGridCard({ cat }) {
  return (
    <Link
      to={cat.path}
      className="group relative overflow-hidden rounded-xl aspect-[4/3] card-hover
        border dark:border-untold-border light:border-gray-200"
    >
      <div className="absolute inset-0 dark:bg-gradient-to-br dark:from-untold-surface dark:to-untold-dark light:bg-gradient-to-br light:from-gray-100 light:to-gray-200" />
      <div className="absolute inset-0 bg-untold-gold/0 group-hover:bg-untold-gold/10 transition-colors duration-300" />
      <div className="relative z-10 flex flex-col justify-end h-full p-4 sm:p-5">
        <h3 className="font-display text-lg sm:text-xl font-bold dark:text-untold-white light:text-black group-hover:text-untold-gold transition-colors">
          {cat.name}
        </h3>
        <p className="mt-1 text-xs sm:text-sm dark:text-untold-muted light:text-gray-500 line-clamp-2">
          {cat.description}
        </p>
      </div>
    </Link>
  );
}

export default function Explore() {
  const [params, setParams] = useSearchParams();
  const [query, setQuery] = useState(params.get('q') || '');
  const [sport, setSport] = useState(params.get('sport') || 'All');
  const [category, setCategory] = useState(params.get('category') || 'all');
  const [vertical, setVertical] = useState(params.get('vertical') || '');

  useEffect(() => {
    const next = new URLSearchParams();
    if (query) next.set('q', query);
    if (sport !== 'All') next.set('sport', sport);
    if (category !== 'all') next.set('category', category);
    if (sort !== 'popular') next.set('sort', sort);
    if (vertical) next.set('vertical', vertical);
    setParams(next, { replace: true });
  }, [query, sport, category, sort, vertical, setParams]);

  const searchResults = useMemo(() => exploreSearch(query), [query]);

  const filteredItems = useMemo(() => {
    let list = query.trim() ? searchResults.videos : videoCatalog;
    if (category !== 'all') list = list.filter((v) => v.category === category);
    if (vertical) list = list.filter((v) => v.vertical === vertical);
    list = filterVideosBySport(list, sport);
    return sortVideos(list, sort);
  }, [query, sport, category, sort, vertical, searchResults.videos]);

  const trending = getTrendingVideos(8);
  const recommended = getRecommendedVideos(8);
  const hasActiveFilters = query.trim() || sport !== 'All' || category !== 'all' || vertical;

  const categoryOptions = useMemo(
    () => [
      { value: 'all', label: 'All' },
      ...EXPLORE_CATEGORIES.map((c) => ({ value: c.slug, label: c.name })),
    ],
    []
  );

  const clearFilters = () => {
    setQuery('');
    setSport('All');
    setCategory('all');
    setSort('popular');
    setVertical('');
  };

  const sortSelect = (
    <select
      value={sort}
      onChange={(e) => setSort(e.target.value)}
      aria-label="Sort content"
      className="rounded-lg px-2 py-1 text-[11px] dark:bg-untold-surface light:bg-white border dark:border-untold-border light:border-gray-200 dark:text-untold-white light:text-black focus:ring-2 focus:ring-untold-gold outline-none"
    >
      {SORT_OPTIONS.map((opt) => (
        <option key={opt.value} value={opt.value}>{opt.label}</option>
      ))}
    </select>
  );

  return (
    <>
      <SEO
        title="Explore"
        description="Discover all UNTOLD content — browse by sport, category, athlete, event, and popularity."
        path="/explore"
      />

      <section className="pt-28 pb-6 sm:pt-36">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-6 max-w-2xl mx-auto">
            <p className="dark:text-untold-gold light:text-untold-gold-dark text-xs font-semibold tracking-[0.3em] uppercase mb-2">
              Discover
            </p>
            <h1 className="font-display text-3xl sm:text-4xl font-bold dark:text-untold-white light:text-black">
              Explore
            </h1>
            <p className="mt-3 text-sm sm:text-base dark:text-untold-muted light:text-gray-600">
              Search athletes, sports, documentaries, and events across UNTOLD.
            </p>
          </div>

          <div className="relative max-w-2xl mx-auto mb-4">
            <SearchIcon className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 dark:text-untold-muted light:text-gray-400" />
            <input
              type="search"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search athlete, sport, documentary, event…"
              aria-label="Search all content"
              className="w-full rounded-full pl-11 pr-5 py-2.5 text-sm
                dark:bg-untold-surface light:bg-gray-50
                dark:border-untold-border light:border-gray-200 border
                dark:text-untold-white light:text-black
                focus:outline-none focus:ring-2 focus:ring-untold-gold"
            />
          </div>

          <ContentFilterBar
            primary={{
              label: 'Sport',
              options: EXPLORE_SPORTS.map((s) => ({ value: s, label: s })),
              active: sport,
              onChange: setSport,
            }}
            secondary={{
              label: 'Type',
              options: categoryOptions,
              active: category,
              onChange: setCategory,
              defaultValue: 'all',
              ariaLabel: 'Filter by content type',
            }}
            resultCount={filteredItems.length}
            resultLabel="titles"
            onClear={clearFilters}
            showClear={hasActiveFilters || sort !== 'popular'}
            trailing={sortSelect}
          />
        </div>
      </section>

      {/* Category grid */}
      <section className="py-10 sm:py-12 dark:bg-untold-surface/30 light:bg-gray-50/50">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <h2 className="font-display text-2xl sm:text-3xl font-bold dark:text-untold-white light:text-black mb-6">
            Browse by Category
          </h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-3 gap-3 sm:gap-4">
            {EXPLORE_CATEGORIES.map((cat) => (
              <CategoryGridCard key={cat.slug} cat={cat} />
            ))}
          </div>
        </div>
      </section>

      {/* Search results: events, news, athletes */}
      {query.trim() && (searchResults.events.length > 0 || searchResults.news.length > 0 || searchResults.athletes.length > 0) && (
        <section className="py-8 px-4 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-7xl space-y-8">
            {searchResults.athletes.length > 0 && (
              <div>
                <h3 className="font-display text-xl font-bold dark:text-untold-white light:text-black mb-4">Athletes</h3>
                <div className="flex gap-4 overflow-x-auto scrollbar-hide">
                  {searchResults.athletes.map((a) => (
                    <Link key={a.id} to={`/video/${a.id}`} className="shrink-0 w-32 text-center group">
                      <img src={a.image} alt="" className="w-20 h-20 rounded-full object-cover mx-auto ring-2 ring-untold-gold/30 group-hover:ring-untold-gold" />
                      <p className="mt-2 text-sm font-medium dark:text-untold-white light:text-black">{a.name}</p>
                      <p className="text-xs dark:text-untold-muted light:text-gray-500">{a.sport}</p>
                    </Link>
                  ))}
                </div>
              </div>
            )}
            {searchResults.events.length > 0 && (
              <div>
                <h3 className="font-display text-xl font-bold dark:text-untold-white light:text-black mb-4">Events</h3>
                <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  {searchResults.events.slice(0, 6).map((e) => (
                    <Link key={e.id} to="/events" className="flex gap-3 p-4 rounded-xl dark:bg-untold-surface light:bg-white border dark:border-untold-border light:border-gray-200 card-hover">
                      <img src={e.thumbnail} alt="" className="w-20 h-14 rounded object-cover shrink-0" />
                      <div className="min-w-0">
                        <p className="font-semibold text-sm dark:text-untold-white light:text-black line-clamp-2">{e.eventName}</p>
                        <p className="text-xs dark:text-untold-muted light:text-gray-500 mt-1">{e.sport} · {e.status}</p>
                      </div>
                    </Link>
                  ))}
                </div>
              </div>
            )}
            {searchResults.news.length > 0 && (
              <div>
                <h3 className="font-display text-xl font-bold dark:text-untold-white light:text-black mb-4">News</h3>
                <div className="grid sm:grid-cols-2 gap-4">
                  {searchResults.news.slice(0, 4).map((n) => (
                    <Link key={n.id} to="/news" className="p-4 rounded-xl dark:bg-untold-surface light:bg-white border dark:border-untold-border light:border-gray-200 card-hover">
                      <p className="text-xs text-untold-gold mb-1">{n.sport}</p>
                      <p className="font-semibold dark:text-untold-white light:text-black">{n.title}</p>
                      <p className="text-sm dark:text-untold-muted light:text-gray-500 mt-1 line-clamp-2">{n.excerpt}</p>
                    </Link>
                  ))}
                </div>
              </div>
            )}
          </div>
        </section>
      )}

      {/* Trending */}
      {!hasActiveFilters && (
        <section className="py-10 sm:py-12">
          <SectionHeader title="Trending Now" subtitle="Most popular videos and stories" />
          <ContentRow>
            {trending.map((item) =>
              item.category === 'shorts' ? (
                <ShortsCard key={item.id} title={item.title} image={item.image} duration={item.duration} to={`/video/${item.id}`} />
              ) : (
                <Link key={item.id} to={`/video/${item.id}`} className="shrink-0">
                  <VideoCard
                    title={item.title}
                    image={item.image}
                    category={item.sport}
                    format={item.format}
                    duration={item.duration}
                    videoId={item.id}
                  />
                </Link>
              )
            )}
          </ContentRow>
        </section>
      )}

      {/* Recommended */}
      {!hasActiveFilters && (
        <section className="py-10 sm:py-12 dark:bg-untold-surface/30 light:bg-gray-50/50">
          <SectionHeader title="Recommended for You" subtitle="Personalized picks based on trending content" />
          <ContentRow>
            {recommended.map((item) => (
              <Link key={item.id} to={`/video/${item.id}`} className="shrink-0">
                <VideoCard
                  title={item.title}
                  image={item.image}
                  category={item.sport}
                  format={item.format}
                  duration={item.duration}
                  videoId={item.id}
                />
              </Link>
            ))}
          </ContentRow>
        </section>
      )}

      {/* Filtered catalog */}
      <section className="py-10 sm:pb-20">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className={CONTENT_GRID_CLASS}>
            {filteredItems.map((item) =>
              item.category === 'shorts' ? (
                <Link key={item.id} to={`/video/${item.id}`} className="flex justify-center sm:block">
                  <ShortsCard title={item.title} image={item.image} duration={item.duration} to={`/video/${item.id}`} />
                </Link>
              ) : (
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
                    fluid
                  />
                </Link>
              )
            )}
          </div>

          {filteredItems.length === 0 && (
            <p className="text-center py-16 dark:text-untold-muted light:text-gray-500">
              No content matches your filters. Try a different sport or search term.
            </p>
          )}
        </div>
      </section>
    </>
  );
}
