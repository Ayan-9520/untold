import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { contentApi } from '../../api/content';
import SectionHeader from '../ui/SectionHeader';
import ContentRow from '../ui/ContentRow';
import VideoCard, { VideoCardSkeleton } from '../ui/VideoCard';

export default function OriginalsRow() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    contentApi.getOriginals().then(({ data }) => {
      setItems(data.filter((v) => v.format !== 'Short').slice(0, 10));
      setLoading(false);
    });
  }, []);

  return (
    <section className="py-12 sm:py-16" aria-labelledby="originals-row-heading">
      <SectionHeader
        title="Originals"
        subtitle="Long-form documentaries & biopics"
        viewAllLink="/originals"
      />
      <ContentRow>
        {loading
          ? [...Array(5)].map((_, i) => <VideoCardSkeleton key={i} />)
          : items.map((item) => (
              <Link key={item.id} to={`/video/${item.id}`} className="shrink-0">
                <VideoCard
                  title={item.title}
                  image={item.image}
                  category={item.sport || item.category}
                  format={item.format}
                  duration={item.duration}
                  trailerUrl={item.trailerUrl}
                  videoId={item.id}
                />
              </Link>
            ))}
      </ContentRow>
    </section>
  );
}
