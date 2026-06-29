import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useEngagement } from '../../context/EngagementContext';
import { useLocale } from '../../context/LocaleContext';
import SectionHeader from '../ui/SectionHeader';
import ContentRow from '../ui/ContentRow';
import VideoCard from '../ui/VideoCard';

export default function RecommendedWidget() {
  const { t } = useTranslation();
  const { recommendations, watchHistory } = useEngagement();
  const { regionalVideos } = useLocale();

  const items = watchHistory.length > 0 ? recommendations : regionalVideos.length > 0 ? regionalVideos : recommendations;

  if (items.length === 0) return null;

  const subtitle = watchHistory.length > 0
    ? `Because you watched ${watchHistory[0]?.title?.split(' ').slice(0, 2).join(' ') || 'similar content'}`
    : t('home.regionalSubtitle');

  return (
    <section className="py-10 sm:py-12" aria-labelledby="recommended">
      <SectionHeader title={t('home.recommended')} subtitle={subtitle} viewAllLink="/explore" />
      <ContentRow>
        {items.map((item) => (
          <Link key={item.id} to={`/video/${item.id}`} className="shrink-0">
            <VideoCard
              title={item.title}
              image={item.image}
              category={item.sport}
              format={item.format}
              duration={item.duration}
              videoId={item.id}
              trailerUrl={item.trailerUrl}
            />
          </Link>
        ))}
      </ContentRow>
    </section>
  );
}
