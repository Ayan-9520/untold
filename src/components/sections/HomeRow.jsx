import { Link } from 'react-router-dom';
import { getByCategory, videoCatalog } from '../../data/videoCatalog';
import {
  getByVertical,
  getAwardWinning,
  getEditorsChoice,
  getLatestReleases,
} from '../../data/verticalCatalog';
import { contentApi } from '../../api/content';
import SectionHeader from '../ui/SectionHeader';
import ContentRow from '../ui/ContentRow';
import VideoCard, { VideoCardSkeleton } from '../ui/VideoCard';
import ShortsCard from '../ui/ShortsCard';
import SectionReveal from '../ui/SectionReveal';
import ContinueWatching from './ContinueWatching';

function resolveItems(row) {
  switch (row.type) {
    case 'trending':
      return videoCatalog.filter((v) => v.trending).slice(0, 10);
    case 'latest':
      return getLatestReleases(10);
    case 'award':
      return getAwardWinning(8);
    case 'editors':
      return getEditorsChoice(8);
    case 'vertical':
      if (row.vertical === 'sports') {
        return [
          ...getByCategory('legends').slice(0, 6),
          ...getByVertical('ufc', 2),
        ].slice(0, 10);
      }
      return getByVertical(row.vertical, 10);
    case 'category':
      return getByCategory(row.category).slice(0, 10);
    default:
      return [];
  }
}

export default function HomeRow({ row }) {
  if (row.type === 'continue') {
    return <ContinueWatching />;
  }

  const items = resolveItems(row);
  const isShorts = row.variant === 'short' || row.category === 'shorts';

  if (!items.length) return null;

  return (
    <SectionReveal className="ott-row" aria-labelledby={`row-${row.type}-${row.vertical || row.category || ''}`}>
      <SectionHeader
        title={row.title}
        subtitle={row.subtitle}
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
                category={item.vertical || item.sport || item.format}
                format={item.format}
                duration={item.duration}
                description={item.description}
                variant={item.category === 'legends' ? 'legend' : 'default'}
                videoId={item.id}
                trailerUrl={item.trailerUrl}
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
