import { useState, useEffect } from 'react';
import { contentApi } from '../../api/content';
import SectionHeader from '../ui/SectionHeader';
import ContentRow from '../ui/ContentRow';
import VideoCard, { VideoCardSkeleton } from '../ui/VideoCard';

export default function Rivalries() {
  const [rivalries, setRivalries] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    contentApi.getRivalries().then(({ data }) => {
      setRivalries(data);
      setLoading(false);
    });
  }, []);

  return (
    <section className="py-12 sm:py-16 dark:bg-untold-surface/50 light:bg-gray-50" aria-labelledby="rivalries-heading">
      <SectionHeader
        title="Rivalries"
        subtitle="When greatness collides"
        viewAllLink="/originals"
      />
      <ContentRow>
        {loading
          ? [...Array(4)].map((_, i) => <VideoCardSkeleton key={i} />)
          : rivalries.map((rivalry) => (
              <VideoCard
                key={rivalry.id}
                title={rivalry.title}
                image={rivalry.image}
                category={`${rivalry.episodes} Episodes`}
                description={rivalry.description}
                variant="rivalry"
              />
            ))}
      </ContentRow>
    </section>
  );
}
