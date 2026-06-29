import { useParams, Link } from 'react-router-dom';
import { useEffect, useState } from 'react';
import SEO from '../components/SEO';
import Button from '../components/ui/Button';
import VideoCard from '../components/ui/VideoCard';
import VideoPlayer from '../components/player/VideoPlayer';
import { PlayIcon, BookmarkIcon } from '../components/icons';
import { getVideoById, videoCatalog } from '../data/videoCatalog';
import { useWatchlist } from '../context/WatchlistContext';
import { useEngagement } from '../context/EngagementContext';
import { useWebAuth } from '../context/WebAuthContext';
import client from '../api/client';

export default function VideoDetail() {
  const { id } = useParams();
  const [video, setVideo] = useState(null);
  const [showPlayer, setShowPlayer] = useState(false);
  const [apiVideoId, setApiVideoId] = useState(null);
  const { isInWatchlist, toggleWatchlist } = useWatchlist();
  const { recordWatch } = useEngagement();
  const { user } = useWebAuth();

  useEffect(() => {
    const mock = getVideoById(id);
    setVideo(mock);

    const numericId = Number(id);
    if (!Number.isNaN(numericId)) {
      client.get(`/videos/${numericId}`).then(({ data }) => {
        setApiVideoId(data.id);
        setVideo((prev) => ({
          ...prev,
          ...mock,
          title: data.title || mock?.title,
          description: data.description || mock?.description,
          accessTier: data.access_tier,
        }));
      }).catch(() => {});
    }
  }, [id]);

  useEffect(() => {
    if (video) recordWatch(video, 0.12);
  }, [video, recordWatch]);

  if (!video) {
    return (
      <div className="pt-32 pb-20 text-center px-4">
        <h1 className="text-2xl font-bold dark:text-untold-white light:text-black">Story not found</h1>
        <Link to="/explore" className="mt-4 inline-block text-untold-gold">Back to Explore</Link>
      </div>
    );
  }

  const related = videoCatalog
    .filter((v) => v.id !== video.id && (v.sport === video.sport || v.category === video.category))
    .slice(0, 6);
  const inList = isInWatchlist(video.id);
  const numericId = Number(id);
  const playVideoId = apiVideoId || (!Number.isNaN(numericId) ? numericId : null);
  const fallbackStream = video.videoUrl || video.trailerUrl;

  return (
    <>
      <SEO title={video.title} description={video.description} path={`/video/${video.id}`} />

      <section className="pt-24 pb-12">
        <div className="relative h-[45vh] min-h-[320px] max-h-[520px] overflow-hidden">
          <img src={video.image || video.thumbnail} alt="" className="absolute inset-0 h-full w-full object-cover" />
          <div className="absolute inset-0 dark:bg-black/60 light:bg-black/50" />
          <div className="absolute inset-0 hero-gradient" />
          <div className="relative z-10 h-full flex items-end">
            <div className="mx-auto w-full max-w-7xl px-4 sm:px-6 lg:px-8 pb-10">
              <div className="flex flex-wrap gap-2 mb-3">
                <span className="text-xs font-semibold uppercase tracking-wider px-2.5 py-1 rounded-full bg-untold-gold text-untold-dark">
                  {video.categoryName || video.category}
                </span>
                {video.sport && (
                  <span className="text-xs font-medium px-2.5 py-1 rounded-full dark:bg-white/10 light:bg-white/20 text-white">
                    {video.sport}
                  </span>
                )}
                {video.accessTier && video.accessTier !== 'free' && (
                  <span className="text-xs font-medium px-2.5 py-1 rounded-full bg-purple-600/80 text-white capitalize">
                    {video.accessTier}
                  </span>
                )}
              </div>
              <h1 className="font-display text-3xl sm:text-5xl font-bold text-white max-w-3xl leading-tight">
                {video.title}
              </h1>
              <p className="mt-2 text-sm text-white/70">
                {video.year} · {video.duration}
              </p>
            </div>
          </div>
        </div>

        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-10">
          <div className="flex flex-wrap gap-3 mb-8">
            <Button
              size="lg"
              icon={<PlayIcon className="w-5 h-5" />}
              onClick={() => {
                if (!user && video.accessTier && video.accessTier !== 'free') {
                  window.location.href = '/login';
                  return;
                }
                setShowPlayer(true);
              }}
            >
              Watch Now
            </Button>
            <Button
              variant="secondary"
              size="lg"
              icon={<BookmarkIcon className="w-5 h-5" filled={inList} />}
              onClick={() => toggleWatchlist(video)}
            >
              {inList ? 'In Watchlist' : 'Add to List'}
            </Button>
            <Link to="/membership">
              <Button variant="outline" size="lg">Go Premium</Button>
            </Link>
          </div>

          {showPlayer && (
            <div className="mb-10">
              <VideoPlayer
                videoId={playVideoId}
                fallbackUrl={fallbackStream}
                poster={video.thumbnail || video.image}
                title={video.title}
              />
            </div>
          )}

          {!showPlayer && video.trailerUrl && (
            <div className="mb-10 rounded-xl overflow-hidden aspect-video max-w-3xl dark:bg-untold-surface light:bg-black">
              <video
                src={video.trailerUrl}
                controls
                poster={video.thumbnail || video.image}
                className="w-full h-full object-cover"
              />
              <p className="text-xs dark:text-untold-muted light:text-gray-500 mt-2 px-1">Trailer preview</p>
            </div>
          )}

          <p className="text-base sm:text-lg dark:text-untold-white/80 light:text-gray-700 leading-relaxed max-w-3xl">
            {video.description}
          </p>

          {related.length > 0 && (
            <div className="mt-14">
              <h2 className="font-display text-2xl font-bold dark:text-untold-white light:text-black mb-6">More Like This</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                {related.map((r) => (
                  <Link key={r.id} to={`/video/${r.id}`}>
                    <VideoCard title={r.title} image={r.image} category={r.sport} duration={r.duration} videoId={r.id} />
                  </Link>
                ))}
              </div>
            </div>
          )}
        </div>
      </section>
    </>
  );
}
