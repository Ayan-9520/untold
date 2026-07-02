import { useState, useEffect } from 'react';
import SEO from '../components/SEO';
import HeroBanner from '../components/sections/HeroBanner';
import HomeRow from '../components/sections/HomeRow';
import MembershipCTA from '../components/sections/MembershipCTA';
import { heroContent } from '../data/heroSlides';
import { HOME_FEATURED_ROWS } from '../data/homeRows';
import { contentApi } from '../api/content';

/**
 * UNTOLD ORIGINALS — Netflix-style premium OTT homepage
 */
export default function Home() {
  const [hero, setHero] = useState(heroContent);

  useEffect(() => {
    contentApi.getHero().then(({ data }) => setHero(data));
  }, []);

  return (
    <>
      <SEO
        title="UNTOLD ORIGINALS"
        description="UNTOLD ORIGINALS — The Story Behind The Glory. Premium global documentary streaming: biopics, true stories, sports legends, business, Hollywood, Bollywood, science, and history."
        path="/"
      />
      <HeroBanner content={hero} />
      <div className="ott-home-rows relative z-10 -mt-4 md:-mt-8">
        {HOME_FEATURED_ROWS.map((row) => (
          <HomeRow key={`${row.type}-${row.vertical || row.category || row.titleKey}`} row={row} />
        ))}
      </div>
      <MembershipCTA />
    </>
  );
}
