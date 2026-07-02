import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { api } from '../../api/client';
import { mapVideo } from '../../api/content';
import SectionHeader from '../ui/SectionHeader';
import ContentRow from '../ui/ContentRow';
import VideoCard, { VideoCardSkeleton } from '../ui/VideoCard';
import ShortsCard from '../ui/ShortsCard';
import SectionReveal from '../ui/SectionReveal';
import ContinueWatching from './ContinueWatching';

async function fetchRowItems(row) {
  const pageSize = row.variant === 'short' || row.category === 'shorts' ? 12 : 10;
  const params = { page_size: pageSize };

  switch (row.type) {
    case 'trending':
      return (await api.videos.list({ ...params, trending: true })).items.map(mapVideo);
    case 'top10':
      return (await api.videos.list({ ...params, trending: true, page_size: 10 })).items.map(mapVideo);
    case 'latest':
      return (await api.videos.list(params)).items.map(mapVideo);
    case 'award':
    case 'editors':
    case 'comingSoon':
      return (await api.videos.list({ ...params, featured: true })).items.map(mapVideo);
    case 'category':
      return (await api.videos.list({ ...params, category: row.category })).items.map(mapVideo);
    case 'vertical':
      if (row.vertical === 'sports') {
        const [legends, ufc] = await Promise.all([
          api.videos.list({ category: 'legends', page_size: 6 }),
          api.videos.list({ category: 'ufc', page_size: 4 }),
        ]);
        return [...legends.items, ...ufc.items].map(mapVideo).slice(0, pageSize);
      }
      return (await api.videos.list({ ...params, category: row.vertical })).items.map(mapVideo);
    default:
      return [];
  }
}

export default function HomeRow({ row }) {
  const { t } = useTranslation();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(row.type !== 'continue');

  useEffect(() => {
    if (row.type === 'continue') return;
    let cancelled = false;
    setLoading(true);
    fetchRowItems(row)
      .then((data) => {
        if (!cancelled) setItems(data);
      })
      .catch(() => {
        if (!cancelled) setItems([]);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => { cancelled = true; };
  }, [row.type, row.category, row.vertical, row.variant]);

  if (row.type === 'continue') {
    return <ContinueWatching />;
  }

  const isShorts = row.variant === 'short' || row.category === 'shorts';

  if (loading) {
    return (
      <div className="ott-row">
        <div className="h-6 w-48 skeleton rounded mb-4 mx-4 sm:mx-8" />
        <ContentRow>
          {[...Array(5)].map((_, i) => (
            <VideoCardSkeleton key={i} />
          ))}
        </ContentRow>
      </div>
    );
  }

  if (!items.length) return null;

  const title = row.titleKey ? t(row.titleKey) : row.title;
  const subtitle = row.subtitleKey ? t(row.subtitleKey) : row.subtitle;

  return (
    <SectionReveal className="ott-row" aria-labelledby={`row-${row.type}-${row.vertical || row.category || ''}`}>
      <SectionHeader
        title={title}
        subtitle={subtitle}
        viewAllLink={row.viewAll}
      />
      <ContentRow>
        {items.map((item) =>
          isShorts ? (
            <ShortsCard
              key={item.id}
              title={item.title}
              image={item.image}
              duration={item.duration}
              to={`/video/${item.id}`}
            />
          ) : (
            <Link key={item.id} to={`/video/${item.id}`} className="shrink-0">
              <VideoCard
                title={item.title}
                image={item.image}
                category={item.vertical || item.sport || item.category || item.format}
                format={item.format || item.videoType}
                duration={item.duration}
                description={item.description}
                variant={row.category === 'legends' ? 'legend' : 'default'}
                videoId={item.id}
                trailerUrl={item.videoUrl}
                rating={item.rating}
              />
            </Link>
          )
        )}
      </ContentRow>
    </SectionReveal>
  );
}

export function HomeRowSkeleton() {
  return (
    <div className="ott-row">
      <div className="h-6 w-48 skeleton rounded mb-4 mx-4 sm:mx-8" />
      <ContentRow>
        {[...Array(5)].map((_, i) => (
          <VideoCardSkeleton key={i} />
        ))}
      </ContentRow>
    </div>
  );
}
