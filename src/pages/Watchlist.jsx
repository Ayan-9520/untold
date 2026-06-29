import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import SEO from '../components/SEO';
import VideoCard, { VideoCardSkeleton } from '../components/ui/VideoCard';
import { useWebAuth } from '../context/WebAuthContext';
import { useWatchlist } from '../context/WatchlistContext';
import { api } from '../api/client';
import { CONTENT_GRID_CLASS } from '../constants/contentLayout';

export default function WatchlistPage() {
  const { isAuthenticated, loading: authLoading } = useWebAuth();
  const { items: localItems } = useWatchlist();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (authLoading) return;
    const load = async () => {
      if (isAuthenticated) {
        try {
          const data = await api.watchlist.list();
          setItems(
            (data.items || []).map((w) => ({
              id: w.video?.id || w.video_id,
              title: w.video?.title,
              image: w.video?.image_url,
              sport: w.video?.category?.name,
              format: w.video?.video_type,
              duration: w.video?.duration,
            }))
          );
        } catch {
          setItems(localItems);
        }
      } else {
        setItems(localItems);
      }
      setLoading(false);
    };
    load();
  }, [isAuthenticated, authLoading, localItems]);

  if (authLoading) return null;

  return (
    <>
      <SEO title="Watchlist" description="Your UNTOLD watchlist" path="/watchlist" />
      <section className="pt-28 pb-16">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="mb-8">
            <h1 className="font-display text-3xl font-bold dark:text-untold-white light:text-black">Watchlist</h1>
            <p className="mt-2 text-sm dark:text-untold-muted light:text-gray-500">
              {isAuthenticated ? 'Synced to your account' : 'Saved locally — '}
              {!isAuthenticated && <Link to="/login" className="text-untold-gold hover:underline">sign in to sync</Link>}
            </p>
          </div>
          <div className={CONTENT_GRID_CLASS}>
            {loading
              ? [...Array(4)].map((_, i) => <VideoCardSkeleton key={i} fluid />)
              : items.map((item) => (
                  <Link key={item.id} to={`/video/${item.id}`} className="block min-w-0">
                    <VideoCard
                      title={item.title}
                      image={item.image}
                      category={item.sport || item.category}
                      format={item.format}
                      duration={item.duration}
                      videoId={item.id}
                      fluid
                    />
                  </Link>
                ))}
          </div>
          {!loading && items.length === 0 && (
            <p className="text-center py-16 dark:text-untold-muted light:text-gray-500">
              Your watchlist is empty. <Link to="/explore" className="text-untold-gold hover:underline">Explore content</Link>
            </p>
          )}
        </div>
      </section>
    </>
  );
}
