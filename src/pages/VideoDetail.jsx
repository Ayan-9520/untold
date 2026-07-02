import { useParams, Link, useSearchParams } from 'react-router-dom';
import { useEffect, useState, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import SEO from '../components/SEO';
import Button from '../components/ui/Button';
import VideoCard from '../components/ui/VideoCard';
import VideoPlayer from '../components/player/VideoPlayer';
import { PlayIcon, BookmarkIcon, ShareIcon } from '../components/icons';
import { getDocumentaryExtras } from '../utils/documentaryExtras';
import { useWatchlist } from '../context/WatchlistContext';
import { useEngagement } from '../context/EngagementContext';
import { useWebAuth } from '../context/WebAuthContext';
import { api } from '../api/client';
import { mapVideo } from '../api/content';
import { useLocalizedContent } from '../hooks/useLocalizedContent';

export default function VideoDetail() {
  const { t } = useTranslation();
  const { localizeVideo, localizeFormat, ui } = useLocalizedContent();
  const { id } = useParams();
  const [searchParams] = useSearchParams();
  const [video, setVideo] = useState(null);
  const [error, setError] = useState(null);
  const [showPlayer, setShowPlayer] = useState(searchParams.get('trailer') === '1');
  const [apiVideoId, setApiVideoId] = useState(null);
  const [related, setRelated] = useState([]);
  const { isInWatchlist, toggleWatchlist } = useWatchlist();
  const { recordWatch } = useEngagement();
  const { user } = useWebAuth();

  useEffect(() => {
    const numericId = Number(id);
    if (Number.isNaN(numericId)) {
      setError('Invalid video id');
      return;
    }
    setError(null);
    api.videos.get(numericId)
      .then((data) => {
        const mapped = mapVideo(data);
        setApiVideoId(data.id);
        setVideo({
          ...mapped,
          slug: mapped.slug || String(data.id),
          image: mapped.image,
          thumbnail: mapped.image,
          trailerUrl: mapped.videoUrl,
          accessTier: data.access_tier,
          category: data.category?.name || mapped.category,
          categorySlug: mapped.categorySlug || data.category?.slug || '',
          sport: data.category?.name || mapped.category,
          subtitleUrl: data.subtitle_url,
          introEndSeconds: data.intro_end_seconds,
          nextVideoId: data.next_video_id,
        });
      })
      .catch((err) => {
        setVideo(null);
        setError(err.message || 'Video not found');
      });
  }, [id]);

  useEffect(() => {
    if (video) recordWatch(video, 0.12);
  }, [video, recordWatch]);

  useEffect(() => {
    if (!video?.categorySlug && !video?.category) return;
    const cat = video.categorySlug || String(video.category).toLowerCase();
    api.videos.list({ category: cat, page_size: 8 })
      .then(({ items }) => {
        setRelated(
          items
            .map(mapVideo)
            .filter((v) => v.id !== video.id)
            .slice(0, 3)
        );
      })
      .catch(() => setRelated([]));
  }, [video]);

  const displayVideo = useMemo(() => (video ? localizeVideo(video) : null), [video, localizeVideo]);
  const displayRelated = useMemo(() => related.map(localizeVideo), [related, localizeVideo]);

  if (error || !displayVideo) {
    return (
      <div className="pt-32 pb-20 text-center px-4">
        <h1 className="text-2xl font-bold dark:text-untold-white light:text-black">
          {error || ui('documentaryNotFound', t('content.ui.documentaryNotFound', 'Documentary not found'))}
        </h1>
        <Link to="/explore" className="mt-4 inline-block text-untold-gold">
          {ui('backExplore', t('content.ui.backExplore', 'Back to Explore'))}
        </Link>
      </div>
    );
  }

  const extras = getDocumentaryExtras(displayVideo);
  const inList = isInWatchlist(displayVideo.id);
  const numericId = Number(id);
  const playVideoId = apiVideoId || (!Number.isNaN(numericId) ? numericId : null);
  const fallbackStream = displayVideo.videoUrl || displayVideo.trailerUrl;

  const handleShare = async () => {
    const url = window.location.href;
    if (navigator.share) {
      await navigator.share({ title: displayVideo.title, url });
    } else {
      await navigator.clipboard.writeText(url);
    }
  };

  return (
    <>
      <SEO
        title={displayVideo.title}
        description={displayVideo.description}
        path={`/video/${displayVideo.id}`}
        jsonLd={{
          '@context': 'https://schema.org',
          '@type': 'VideoObject',
          name: displayVideo.title,
          description: displayVideo.description,
          thumbnailUrl: displayVideo.image || displayVideo.thumbnail,
          uploadDate: displayVideo.year ? `${displayVideo.year}-01-01` : undefined,
          contentUrl: displayVideo.videoUrl,
          inLanguage: displayVideo.language || 'en',
          genre: displayVideo.sport || displayVideo.category,
        }}
      />

      <section className="doc-detail pt-[calc(var(--nav-height-mobile)+var(--lang-bar-height))] md:pt-[calc(var(--nav-height)+var(--lang-bar-height))]">
        <div className="relative h-[50vh] min-h-[360px] max-h-[600px] overflow-hidden">
          <img src={displayVideo.image || displayVideo.thumbnail} alt="" className="absolute inset-0 h-full w-full object-cover" />
          <div className="absolute inset-0 bg-gradient-to-t from-untold-dark via-untold-dark/70 to-untold-dark/30" />
          <div className="relative z-10 h-full flex items-end">
            <div className="mx-auto w-full max-w-7xl px-4 sm:px-6 lg:px-8 pb-10">
              <p className="text-xs font-bold uppercase tracking-[0.35em] text-untold-gold mb-3">UNTOLD ORIGINALS</p>
              <div className="flex flex-wrap gap-2 mb-3">
                <span className="doc-badge doc-badge--gold">{localizeFormat(displayVideo.format || 'Documentary')}</span>
                {displayVideo.vertical && <span className="doc-badge">{displayVideo.vertical}</span>}
                {displayVideo.sport && <span className="doc-badge">{displayVideo.sport}</span>}
                <span className="doc-badge">4K</span>
                {displayVideo.rating && <span className="doc-badge">{displayVideo.rating}</span>}
              </div>
              <h1 className="font-display text-3xl sm:text-5xl lg:text-6xl font-bold text-white max-w-4xl leading-tight">
                {displayVideo.title}
              </h1>
              <p className="mt-3 text-sm text-white/70 flex flex-wrap gap-x-3 gap-y-1">
                <span>{displayVideo.year}</span>
                <span>·</span>
                <span>{displayVideo.duration}</span>
                <span>·</span>
                <span>{displayVideo.language || t('selectors.language')}</span>
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
                if (!user && displayVideo.accessTier && displayVideo.accessTier !== 'free') {
                  window.location.href = '/login';
                  return;
                }
                setShowPlayer(true);
              }}
            >
              {t('hero.watchNow')}
            </Button>
            <Button variant="secondary" size="lg" onClick={() => setShowPlayer(true)}>
              {t('hero.watchTrailer')}
            </Button>
            <Button
              variant="secondary"
              size="lg"
              icon={<BookmarkIcon className="w-5 h-5" filled={inList} />}
              onClick={() => toggleWatchlist(displayVideo)}
            >
              {inList ? ui('inWatchlist', t('content.ui.inWatchlist', 'In Watchlist')) : ui('addWatchlist', t('content.ui.addWatchlist', 'Add to Watchlist'))}
            </Button>
            <Button variant="outline" size="lg" icon={<ShareIcon className="w-5 h-5" />} onClick={handleShare}>
              {t('common.share')}
            </Button>
            <Link to="/membership">
              <Button variant="outline" size="lg">{t('common.goPremium')}</Button>
            </Link>
          </div>

          {showPlayer && (
            <div className="mb-12 doc-player-wrap">
              <VideoPlayer
                videoId={playVideoId}
                fallbackUrl={fallbackStream}
                poster={displayVideo.thumbnail || displayVideo.image}
                title={displayVideo.title}
                subtitleUrl={displayVideo.subtitleUrl}
                introEndSeconds={displayVideo.introEndSeconds}
                nextVideoId={displayVideo.nextVideoId}
              />
            </div>
          )}

          <div className="grid lg:grid-cols-3 gap-10">
            <div className="lg:col-span-2 space-y-10">
              <section>
                <h2 className="doc-section-title">{t('common.synopsis')}</h2>
                <p className="text-base sm:text-lg dark:text-untold-white/85 light:text-gray-700 leading-relaxed">
                  {extras.synopsis}
                </p>
              </section>

              {extras.episodes && (
                <section>
                  <h2 className="doc-section-title">{t('common.episodes')}</h2>
                  <ul className="space-y-3">
                    {extras.episodes.map((ep) => (
                      <li key={ep.n} className="doc-episode-card">
                        <span className="doc-episode-num">{ep.n}</span>
                        <div>
                          <p className="font-semibold dark:text-white light:text-black">{ep.title}</p>
                          <p className="text-sm dark:text-untold-muted light:text-gray-500">{ep.duration} · {ep.description}</p>
                        </div>
                        <Button size="sm" variant="secondary">{ui('play', t('content.ui.play', 'Play'))}</Button>
                      </li>
                    ))}
                  </ul>
                </section>
              )}

              <section>
                <h2 className="doc-section-title">{ui('timeline', t('content.ui.timeline', 'Timeline'))}</h2>
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
                <h2 className="doc-section-title">{t('common.castCredits')}</h2>
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
                <h2 className="doc-section-title">{ui('sources', t('content.ui.sources', 'Sources & References'))}</h2>
                <ul className="space-y-2 text-sm dark:text-untold-muted light:text-gray-600">
                  {extras.sources.map((s) => (
                    <li key={s}>• {s}</li>
                  ))}
                </ul>
              </section>

              <section className="doc-side-card">
                <h2 className="doc-section-title">{ui('gallery', t('content.ui.gallery', 'Gallery'))}</h2>
                <div className="grid grid-cols-2 gap-2">
                  {extras.gallery.map((src, i) => (
                    <img key={i} src={src} alt="" className="rounded-lg aspect-video object-cover" loading="lazy" />
                  ))}
                </div>
              </section>
            </aside>
          </div>

          {displayRelated.length > 0 && (
            <div className="mt-16 pt-10 border-t dark:border-untold-border light:border-gray-200">
              <h2 className="font-display text-2xl font-bold dark:text-untold-white light:text-black mb-6">
                {ui('relatedStories', t('content.ui.relatedStories', 'Related Stories'))}
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                {displayRelated.map((r) => (
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
