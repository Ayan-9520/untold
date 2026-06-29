import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import newsApi from '../../api/news';

export default function BreakingNewsTicker() {
  const [headlines, setHeadlines] = useState([]);

  useEffect(() => {
    newsApi.latest(8).then(({ items }) => setHeadlines(items));
  }, []);

  if (headlines.length === 0) return null;

  const items = [...headlines, ...headlines];

  return (
    <div
      className="relative overflow-hidden border-b dark:border-red-900/30 light:border-red-200
        dark:bg-red-950/40 light:bg-red-50"
      aria-label="Breaking news"
    >
      <div className="flex items-center">
        <span className="shrink-0 z-10 px-4 py-2.5 text-xs font-bold uppercase tracking-wider
          bg-red-600 text-white flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-white animate-pulse" />
          Breaking
        </span>
        <div className="flex-1 overflow-hidden py-2.5">
          <div className="flex animate-marquee whitespace-nowrap">
            {items.map((item, i) => (
              <Link
                key={`${item.id}-${i}`}
                to={`/news/${item.id}`}
                className="inline-flex items-center mx-6 text-sm dark:text-untold-white/90 light:text-gray-800 hover:text-untold-gold transition-colors"
              >
                <span className="text-red-500 font-semibold mr-2">{item.sport}</span>
                {item.title}
                <span className="mx-6 text-untold-gold/50">•</span>
              </Link>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
