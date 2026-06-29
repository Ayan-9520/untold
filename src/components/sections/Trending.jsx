import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { contentApi } from '../../api/content';
import SectionHeader from '../ui/SectionHeader';
import ContentRow from '../ui/ContentRow';
import VideoCard, { VideoCardSkeleton } from '../ui/VideoCard';
import SectionReveal from '../ui/SectionReveal';
import Badge from '../ui/Badge';

export default function Trending() {
  const [trending, setTrending] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    contentApi.getTrending().then(({ data }) => {
      setTrending(data);
      setLoading(false);
    });
  }, []);

  return (
    <SectionReveal className="py-12 sm:py-16" aria-labelledby="trending-heading">
      <SectionHeader
        title="Trending Originals"
        subtitle="Premium documentaries everyone is watching"
        viewAllLink="/originals"
      />
      <ContentRow>
        {loading
          ? [...Array(5)].map((_, i) => <VideoCardSkeleton key={i} />)
          : trending.map((item) => (
              <Link key={item.id} to={`/video/${item.id}`} className="shrink-0 group">
                <div className="relative">
                  <VideoCard
                    title={item.title}
                    image={item.image}
                    category={item.category || item.sport}
                    duration={item.duration}
                    videoId={item.id}
                    trailerUrl={item.trailerUrl}
                    rating={item.rating}
                  />
                  {item.trending && (
                    <Badge variant="gold" size="sm" className="absolute top-2 left-2 z-10">
                      Trending
                    </Badge>
                  )}
                </div>
              </Link>
            ))}
      </ContentRow>
    </SectionReveal>
  );
}
