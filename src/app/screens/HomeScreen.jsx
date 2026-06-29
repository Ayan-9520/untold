import { useState, useEffect } from 'react';
import MobileHero from '../components/MobileHero';
import ContentCarousel from '../components/ContentCarousel';
import MobileVideoCard, { MobileVideoCardSkeleton } from '../components/MobileVideoCard';
import { contentApi } from '../../api/content';

export default function HomeScreen() {
  const [featured, setFeatured] = useState(null);
  const [trending, setTrending] = useState([]);
  const [legends, setLegends] = useState([]);
  const [rivalries, setRivalries] = useState([]);
  const [shorts, setShorts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      contentApi.getFeatured(),
      contentApi.getTrending(),
      contentApi.getLegends(),
      contentApi.getRivalries(),
      contentApi.getShorts(),
    ]).then(([feat, trend, leg, riv, sh]) => {
      setFeatured(feat.data);
      setTrending(trend.data);
      setLegends(leg.data);
      setRivalries(riv.data);
      setShorts(sh.data.slice(0, 6));
      setLoading(false);
    });
  }, []);

  return (
    <div className="pb-20 animate-fade-in">
      <MobileHero content={featured} />

      <div className="mt-2">
        <ContentCarousel title="Trending Now" subtitle="Popular this week">
          {loading
            ? [...Array(4)].map((_, i) => <MobileVideoCardSkeleton key={i} />)
            : trending.map((item) => <MobileVideoCard key={item.id} item={item} />)}
        </ContentCarousel>

        <ContentCarousel title="Legends" subtitle="Icons of the game">
          {loading
            ? [...Array(4)].map((_, i) => <MobileVideoCardSkeleton key={i} />)
            : legends.map((item) => (
                <MobileVideoCard
                  key={item.id}
                  item={{ ...item, title: item.subtitle, image: item.image }}
                />
              ))}
        </ContentCarousel>

        <ContentCarousel title="Rivalries" subtitle="When greatness collides">
          {loading
            ? [...Array(4)].map((_, i) => <MobileVideoCardSkeleton key={i} />)
            : rivalries.map((item) => <MobileVideoCard key={item.id} item={item} />)}
        </ContentCarousel>

        <ContentCarousel title="Shorts" subtitle="Quick hits">
          {loading
            ? [...Array(4)].map((_, i) => <MobileVideoCardSkeleton key={i} variant="short" />)
            : shorts.map((item, i) => (
                <MobileVideoCard key={item.id} item={item} variant="short" index={i} />
              ))}
        </ContentCarousel>
      </div>
    </div>
  );
}
