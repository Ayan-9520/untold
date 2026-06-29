import { useState, useEffect } from 'react';
import { contentApi } from '../../api/content';
import SectionHeader from '../ui/SectionHeader';
import ContentRow from '../ui/ContentRow';
import ShortsCard from '../ui/ShortsCard';

export default function ShortsSection() {
  const [shorts, setShorts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    contentApi.getShorts().then(({ data }) => {
      setShorts(data);
      setLoading(false);
    });
  }, []);

  return (
    <section className="py-12 sm:py-16 dark:bg-untold-surface/50 light:bg-gray-50" aria-labelledby="shorts-heading">
      <SectionHeader
        title="Shorts"
        subtitle="Bite-sized moments of glory"
        viewAllLink="/shorts"
        viewAllText="See All Shorts"
      />
      <ContentRow>
        {loading
          ? [...Array(6)].map((_, i) => (
              <div key={i} className="w-[140px] shrink-0 aspect-[9/14] rounded-xl skeleton" />
            ))
          : shorts.map((short) => (
              <ShortsCard
                key={short.id}
                title={short.title}
                image={short.image}
                duration={short.duration}
                views={short.views}
              />
            ))}
      </ContentRow>
    </section>
  );
}
