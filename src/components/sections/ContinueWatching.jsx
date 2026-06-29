import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import SectionHeader from '../ui/SectionHeader';
import streamingApi from '../../api/streaming';

export default function ContinueWatching() {
  const [items, setItems] = useState([]);

  useEffect(() => {
    streamingApi.getContinueWatching(8).then(setItems);
  }, []);

  if (!items.length) return null;

  return (
    <section className="py-10 sm:py-12">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <SectionHeader title="Continue Watching" subtitle="Pick up where you left off" />
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
          {items.map((item) => (
            <Link
              key={item.video_id}
              to={`/video/${item.video_id}`}
              className="group rounded-xl overflow-hidden border dark:border-untold-border light:border-gray-200 card-hover"
            >
              <div className="relative aspect-video">
                <img src={item.image_url} alt="" className="h-full w-full object-cover" loading="lazy" />
                <div className="absolute bottom-0 left-0 right-0 h-1 bg-white/20">
                  <div
                    className="h-full bg-untold-gold"
                    style={{ width: `${Math.min(item.progress_percent, 100)}%` }}
                  />
                </div>
              </div>
              <p className="p-3 text-sm font-semibold dark:text-untold-white light:text-black line-clamp-2 group-hover:text-untold-gold transition-colors">
                {item.title}
              </p>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}
