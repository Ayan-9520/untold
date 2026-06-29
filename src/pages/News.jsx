import { useEffect, useMemo, useState } from 'react';
import SEO from '../components/SEO';
import ContentFilterBar from '../components/ui/ContentFilterBar';
import NewsCard from '../components/news/NewsCard';
import Loader from '../components/ui/Loader';
import newsApi from '../api/news';
import { buildSportCounts, filterBySport, toSportOptions } from '../utils/contentFilters';

const NEWS_SPORTS = ['All', 'Cricket', 'Football', 'Tennis', 'Formula 1', 'MMA', 'Olympics'];

export default function News() {
  const [sport, setSport] = useState('All');
  const [articles, setArticles] = useState([]);
  const [trending, setTrending] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    async function load() {
      setLoading(true);
      const [listRes, trendRes] = await Promise.all([
        newsApi.list({ page: 1, page_size: 30 }),
        newsApi.trending(6),
      ]);
      if (!active) return;
      setArticles(listRes.items);
      setTrending(trendRes.items);
      setLoading(false);
    }
    load();
    return () => { active = false; };
  }, []);

  const sportCounts = useMemo(() => buildSportCounts(articles), [articles]);

  const filtered = useMemo(() => {
    const list = filterBySport(articles, sport);
    return list.sort((a, b) => new Date(b.publishedAt) - new Date(a.publishedAt));
  }, [articles, sport]);

  const featured = filtered[0];
  const showTrending = sport === 'All' && trending.length > 0;

  if (loading) return <Loader fullScreen label="Loading news" />;

  return (
    <>
      <SEO
        title="News"
        description="Latest sports news on UNTOLD — cricket, football, tennis, F1, and global sports coverage."
        path="/news"
      />

      <section className="pt-28 pb-6 sm:pt-36">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-6 max-w-2xl mx-auto">
            <p className="dark:text-untold-gold light:text-untold-gold-dark text-xs font-semibold tracking-[0.3em] uppercase mb-2">
              Sports Desk
            </p>
            <h1 className="font-display text-3xl sm:text-4xl font-bold dark:text-untold-white light:text-black">
              News
            </h1>
            <p className="mt-3 text-sm sm:text-base dark:text-untold-muted light:text-gray-600">
              Breaking stories, match reports, and analysis from the world of sport.
            </p>
          </div>

          <ContentFilterBar
            primary={{
              label: 'Sport',
              options: toSportOptions(NEWS_SPORTS, sportCounts),
              active: sport,
              onChange: setSport,
            }}
            resultCount={filtered.length}
            resultLabel="articles"
            onClear={() => setSport('All')}
          />
        </div>
      </section>

      {featured && (
        <section className="pb-10 px-4 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-7xl">
            <NewsCard article={featured} featured />
            <p className="mt-4 text-sm dark:text-untold-muted light:text-gray-600 max-w-3xl">
              {featured.excerpt}
            </p>
          </div>
        </section>
      )}

      {showTrending && (
        <section className="pb-10 px-4 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-7xl">
            <h2 className="font-display text-2xl font-bold dark:text-untold-white light:text-black mb-6">Trending</h2>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 sm:gap-6">
              {trending.slice(0, 3).map((article) => (
                <NewsCard key={article.id} article={article} />
              ))}
            </div>
          </div>
        </section>
      )}

      <section className="pb-20 px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <h2 className="font-display text-2xl font-bold dark:text-untold-white light:text-black mb-6">Latest</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
            {filtered.slice(sport === 'All' && featured ? 1 : 0).map((article) => (
              <NewsCard key={article.id} article={article} />
            ))}
          </div>
          {filtered.length === 0 && (
            <p className="text-center py-12 dark:text-untold-muted light:text-gray-500">No news for this sport yet.</p>
          )}
        </div>
      </section>
    </>
  );
}
