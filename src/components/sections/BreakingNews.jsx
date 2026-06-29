import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import newsApi from '../../api/news';
import SectionHeader from '../ui/SectionHeader';
import BreakingNewsTicker from '../engagement/BreakingNewsTicker';
import Badge from '../ui/Badge';
import SectionReveal from '../ui/SectionReveal';

export default function BreakingNews() {
  const [breaking, setBreaking] = useState([]);
  const [latest, setLatest] = useState([]);

  useEffect(() => {
    Promise.all([newsApi.trending(4), newsApi.latest(3)]).then(([trendRes, latestRes]) => {
      setBreaking(trendRes.items);
      setLatest(latestRes.items);
    });
  }, []);

  return (
    <SectionReveal className="section-cinematic py-10 sm:py-14" aria-labelledby="breaking-news">
      <BreakingNewsTicker />
      <SectionHeader title="Breaking News" subtitle="Latest from the UNTOLD sports desk" viewAllLink="/news" />
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6">
          {breaking[0] && (
            <Link
              to={`/news/${breaking[0].id}`}
              className="lg:col-span-2 group relative rounded-xl overflow-hidden aspect-[16/9] lg:aspect-auto lg:min-h-[260px] card-premium"
            >
              <img src={breaking[0].thumbnail} alt="" className="absolute inset-0 h-full w-full object-cover transition-transform duration-700 group-hover:scale-105" />
              <div className="absolute inset-0 bg-gradient-to-t from-black/95 via-black/45 to-black/20" />
              <Badge variant="breaking" size="sm" pulse className="absolute top-4 left-4">
                Breaking
              </Badge>
              <div className="absolute bottom-0 left-0 right-0 p-5 sm:p-6">
                <p className="text-xs text-untold-gold-light mb-2 font-semibold uppercase tracking-wider">{breaking[0].sport}</p>
                <h3 className="font-display text-xl sm:text-2xl font-bold text-white group-hover:text-untold-gold-light transition-colors">
                  {breaking[0].title}
                </h3>
                <p className="mt-2 text-sm text-white/75 line-clamp-2">{breaking[0].excerpt}</p>
              </div>
            </Link>
          )}
          <div className="flex flex-col gap-3">
            {latest.map((item) => (
              <Link
                key={item.id}
                to={`/news/${item.id}`}
                className="flex gap-3 p-3 rounded-xl dark:bg-untold-surface light:bg-white border dark:border-untold-border light:border-gray-200 card-premium group"
              >
                <img src={item.thumbnail} alt="" className="w-20 h-14 rounded-lg object-cover shrink-0" />
                <div className="min-w-0">
                  <p className="text-[10px] font-semibold uppercase text-untold-gold">{item.sport}</p>
                  <p className="text-sm font-semibold dark:text-untold-white light:text-black line-clamp-2 group-hover:text-untold-gold transition-colors">
                    {item.title}
                  </p>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </div>
    </SectionReveal>
  );
}
