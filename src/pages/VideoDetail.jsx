import { useParams, Link, useSearchParams } from 'react-router-dom';
import { useEffect, useState } from 'react';
import SEO from '../components/SEO';
import Button from '../components/ui/Button';
import VideoCard from '../components/ui/VideoCard';
import VideoPlayer from '../components/player/VideoPlayer';
import { PlayIcon, BookmarkIcon, ShareIcon } from '../components/icons';
import { getVideoById, videoCatalog } from '../data/videoCatalog';
import { getDocumentaryExtras } from '../data/documentaryExtras';
import { useWatchlist } from '../context/WatchlistContext';
import { useEngagement } from '../context/EngagementContext';
import { useWebAuth } from '../context/WebAuthContext';
import client from '../api/client';

export default function VideoDetail() {
  const { id } = useParams();
  const [searchParams] = useSearchParams();
  const [video, setVideo] = useState(null);
  const [showPlayer, setShowPlayer] = useState(searchParams.get('trailer') === '1');
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
        <h1 className="text-2xl font-bold dark:text-untold-white light:text-black">Documentary not found</h1>
        <Link to="/explore" className="mt-4 inline-block text-untold-gold">Back to Explore</Link>
      </div>
    );
  }

  const extras = getDocumentaryExtras(video);
  const related = videoCatalog
    .filter((v) => v.id !== video.id && (v.vertical === video.vertical || v.sport === video.sport || v.category === video.category))
    .slice(0, 6);
  const inList = isInWatchlist(video.id);
  const numericId = Number(id);
  const playVideoId = apiVideoId || (!Number.isNaN(numericId) ? numericId : null);
  const fallbackStream = video.videoUrl || video.trailerUrl;

  const handleShare = async () => {
    const url = window.location.href;
    if (navigator.share) {
      await navigator.share({ title: video.title, url });
    } else {
      await navigator.clipboard.writeText(url);
    }
  };

  return (
    <>
      <SEO title={video.title} description={video.description} path={`/video/${video.id}`} />

      <section className="doc-detail pt-[var(--nav-height-mobile)] md:pt-[var(--nav-height)]">
        {/* Cinematic banner */}
        <div className="relative h-[50vh] min-h-[360px] max-h-[600px] overflow-hidden">
          <img src={video.image || video.thumbnail} alt="" className="absolute inset-0 h-full w-full object-cover" />
          <div className="absolute inset-0 bg-gradient-to-t from-untold-dark via-untold-dark/70 to-untold-dark/30" />
          <div className="relative z-10 h-full flex items-end">
            <div className="mx-auto w-full max-w-7xl px-4 sm:px-6 lg:px-8 pb-10">
              <p className="text-xs font-bold uppercase tracking-[0.35em] text-untold-gold mb-3">UNTOLD ORIGINALS</p>
              <div className="flex flex-wrap gap-2 mb-3">
                <span className="doc-badge doc-badge--gold">{video.format || 'Documentary'}</span>
                {video.vertical && <span className="doc-badge">{video.vertical}</span>}
                {video.sport && <span className="doc-badge">{video.sport}</span>}
                <span className="doc-badge">4K</span>
                {video.rating && <span className="doc-badge">{video.rating}</span>}
              </div>
              <h1 className="font-display text-3xl sm:text-5xl lg:text-6xl font-bold text-white max-w-4xl leading-tight">
                {video.title}
              </h1>
              <p className="mt-3 text-sm text-white/70 flex flex-wrap gap-x-3 gap-y-1">
                <span>{video.year}</span>
                <span>·</span>
                <span>{video.duration}</span>
                <span>·</span>
                <span>{video.language || 'English'}</span>
                {extras.genres?.slice(0, 3).map((g) => (
                  <span key={g}>· {g}</span>
                ))}
              </p>
            </div>
          </div>
        </div>

        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-10">
          <div className="flex flex-wrap gap-3 mb-10">
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
            <Button variant="secondary" size="lg" onClick={() => setShowPlayer(true)}>
              Watch Trailer
            </Button>
            <Button
              variant="secondary"
              size="lg"
              icon={<BookmarkIcon className="w-5 h-5" filled={inList} />}
              onClick={() => toggleWatchlist(video)}
            >
              {inList ? 'In Watchlist' : 'Add to Watchlist'}
            </Button>
            <Button variant="outline" size="lg" icon={<ShareIcon className="w-5 h-5" />} onClick={handleShare}>
              Share
            </Button>
            <Link to="/membership">
              <Button variant="outline" size="lg">Go Premium</Button>
            </Link>
          </div>

          {showPlayer && (
            <div className="mb-12 doc-player-wrap">
              <VideoPlayer
                videoId={playVideoId}
                fallbackUrl={fallbackStream}
                poster={video.thumbnail || video.image}
                title={video.title}
              />
            </div>
          )}

          <div className="grid lg:grid-cols-3 gap-10">
            <div className="lg:col-span-2 space-y-10">
              <section>
                <h2 className="doc-section-title">Synopsis</h2>
                <p className="text-base sm:text-lg dark:text-untold-white/85 light:text-gray-700 leading-relaxed">
                  {extras.synopsis}
                </p>
              </section>

              {extras.episodes && (
                <section>
                  <h2 className="doc-section-title">Episodes</h2>
                  <ul className="space-y-3">
                    {extras.episodes.map((ep) => (
                      <li key={ep.n} className="doc-episode-card">
                        <span className="doc-episode-num">{ep.n}</span>
                        <div>
                          <p className="font-semibold dark:text-white light:text-black">{ep.title}</p>
                          <p className="text-sm dark:text-untold-muted light:text-gray-500">{ep.duration} · {ep.description}</p>
                        </div>
                        <Button size="sm" variant="secondary">Play</Button>
                      </li>
                    ))}
                  </ul>
                </section>
              )}

              <section>
                <h2 className="doc-section-title">Timeline</h2>
                <ol className="doc-timeline">
                  {extras.timeline.map((t) => (
                    <li key={t.year}>
                      <span className="doc-timeline-year">{t.year}</span>
                      <span className="dark:text-untold-white/80 light:text-gray-700">{t.event}</span>
                    </li>
                  ))}
                </ol>
              </section>
            </div>

            <aside className="space-y-8">
              <section className="doc-side-card">
                <h2 className="doc-section-title">Cast & Credits</h2>
                <ul className="space-y-2">
                  {extras.cast.map((c) => (
                    <li key={c.role} className="flex justify-between text-sm">
                      <span className="dark:text-untold-muted light:text-gray-500">{c.role}</span>
                      <span className="dark:text-white light:text-black font-medium">{c.name}</span>
                    </li>
                  ))}
                </ul>
              </section>

              <section className="doc-side-card">
                <h2 className="doc-section-title">Sources & References</h2>
                <ul className="space-y-2 text-sm dark:text-untold-muted light:text-gray-600">
                  {extras.sources.map((s) => (
                    <li key={s}>• {s}</li>
                  ))}
                </ul>
              </section>

              <section className="doc-side-card">
                <h2 className="doc-section-title">Gallery</h2>
                <div className="grid grid-cols-2 gap-2">
                  {extras.gallery.map((src, i) => (
                    <img key={i} src={src} alt="" className="rounded-lg aspect-video object-cover" loading="lazy" />
                  ))}
                </div>
              </section>
            </aside>
          </div>

          {related.length > 0 && (
            <div className="mt-16 pt-10 border-t dark:border-untold-border light:border-gray-200">
              <h2 className="font-display text-2xl font-bold dark:text-untold-white light:text-black mb-6">
                Related Stories
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                {related.map((r) => (
                  <Link key={r.id} to={`/video/${r.id}`}>
                    <VideoCard title={r.title} image={r.image} category={r.vertical || r.sport} duration={r.duration} videoId={r.id} />
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
