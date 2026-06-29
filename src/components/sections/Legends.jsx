import { useState, useEffect } from 'react';
import { contentApi } from '../../api/content';
import SectionHeader from '../ui/SectionHeader';
import ContentRow from '../ui/ContentRow';
import VideoCard, { VideoCardSkeleton } from '../ui/VideoCard';

export default function Legends() {
  const [legends, setLegends] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    contentApi.getLegends().then(({ data }) => {
      setLegends(data);
      setLoading(false);
    });
  }, []);

  return (
    <section className="py-12 sm:py-16" aria-labelledby="legends-heading">
      <SectionHeader
        title="Legends"
        subtitle="Icons who defined their sport"
        viewAllLink="/originals"
      />
      <ContentRow>
        {loading
          ? [...Array(5)].map((_, i) => <VideoCardSkeleton key={i} />)
          : legends.map((legend) => (
              <VideoCard
                key={legend.id}
                title={legend.subtitle}
                image={legend.image}
                category={legend.title}
                description={legend.description}
                variant="legend"
              />
            ))}
      </ContentRow>
    </section>
  );
}
