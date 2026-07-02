import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../../api/client';
import { mapVideo } from '../../api/content';
import SectionHeader from '../ui/SectionHeader';
import ContentRow from '../ui/ContentRow';
import VideoCard, { VideoCardSkeleton } from '../ui/VideoCard';
import ShortsCard from '../ui/ShortsCard';
import SectionReveal from '../ui/SectionReveal';

export default function CategoryRow({
  category,
  title,
  subtitle,
  viewAllLink,
  limit = 8,
  variant = 'default',
}) {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    const params = { page_size: limit };
    if (category === 'shorts') params.video_type = 'short';
    else params.category = category;

    api.videos.list(params)
      .then((data) => setItems(data.items.map(mapVideo)))
      .catch(() => setItems([]))
      .finally(() => setLoading(false));
  }, [category, limit]);

  const isShorts = category === 'shorts' || variant === 'short';
  if (!loading && items.length === 0) return null;

  return (
    <SectionReveal className={`py-12 sm:py-16 ${category === 'shorts' ? 'dark:bg-untold-surface/50 light:bg-gray-50' : ''}`} aria-labelledby={`${category}-row`}>
      <SectionHeader title={title} subtitle={subtitle} viewAllLink={viewAllLink} />
      <ContentRow>
        {loading
          ? [...Array(5)].map((_, i) =>
              isShorts ? (
                <div key={i} className="w-[140px] shrink-0 aspect-[9/14] rounded-xl skeleton" />
              ) : (
                <VideoCardSkeleton key={i} />
              )
            )
          : items.map((item) =>
              isShorts ? (
                <ShortsCard
                  key={item.id}
                  title={item.title}
                  image={item.image}
                  duration={item.duration}
                  to="/shorts"
                />
              ) : (
                <Link key={item.id} to={`/video/${item.id}`} className="shrink-0">
                  <VideoCard
                    title={item.title}
                    image={item.image}
                    category={item.category || item.sport}
                    format={item.format || item.videoType}
                    duration={item.duration}
                    description={item.description}
                    variant={category === 'legends' ? 'legend' : category === 'rivalries' ? 'rivalry' : 'default'}
                    videoId={item.id}
                    trailerUrl={item.videoUrl}
                    rating={item.rating}
                    showDescription={category === 'legends' || category === 'rivalries'}
                  />
                </Link>
              )
            )}
      </ContentRow>
    </SectionReveal>
  );
}
