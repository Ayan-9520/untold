import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useLocale } from '../../context/LocaleContext';
import SectionHeader from '../ui/SectionHeader';
import ContentRow from '../ui/ContentRow';
import VideoCard from '../ui/VideoCard';
import ShortsCard from '../ui/ShortsCard';

export default function RegionalSpotlight() {
  const { t } = useTranslation();
  const { region, regionalVideos } = useLocale();

  if (regionalVideos.length === 0) return null;

  return (
    <section className="py-10 sm:py-12 border-b dark:border-untold-border/50 light:border-gray-200" aria-labelledby="regional-spotlight">
      <SectionHeader
        title={t('home.regionalFeatured', { region: region.label })}
        subtitle={t('home.regionalSubtitle')}
        viewAllLink="/explore"
      />
      <div className="px-4 sm:px-6 lg:px-8 mb-4">
        <div className="flex flex-wrap gap-2">
          {region.sports.map((sport) => (
            <span
              key={sport}
              className="px-3 py-1 rounded-full text-xs font-medium bg-untold-gold/15 text-untold-gold border border-untold-gold/30"
            >
              {sport}
            </span>
          ))}
        </div>
      </div>
      <ContentRow>
        {regionalVideos.map((item) =>
          item.category === 'shorts' ? (
            <ShortsCard key={item.id} title={item.title} image={item.image} duration={item.duration} to={`/video/${item.id}`} />
          ) : (
            <Link key={item.id} to={`/video/${item.id}`} className="shrink-0">
              <VideoCard
                title={item.title}
                image={item.image}
                category={item.sport}
                format={item.format}
                duration={item.duration}
                videoId={item.id}
              />
            </Link>
          )
        )}
      </ContentRow>
    </section>
  );
}
