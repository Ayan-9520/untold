import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import SEO from '../components/SEO';
import HeroBanner from '../components/sections/HeroBanner';
import LiveNow from '../components/sections/LiveNow';
import Trending from '../components/sections/Trending';
import BreakingNews from '../components/sections/BreakingNews';
import CategoryRow from '../components/sections/CategoryRow';
import RivalriesRow from '../components/sections/RivalriesRow';
import FanWarsRow from '../components/fan/FanWarsRow';
import MembershipCTA from '../components/sections/MembershipCTA';
import PlatformFeatures from '../components/sections/PlatformFeatures';
import { heroContent } from '../data/heroSlides';
import { contentApi } from '../api/content';

/**
 * UNTOLD Premium OTT Homepage
 * Hero → Live → Trending Originals → Shorts → Breaking News → Pillars → Fan Wars → Membership
 */
export default function Home() {
  const { t } = useTranslation();
  const [hero, setHero] = useState(heroContent);

  useEffect(() => {
    contentApi.getHero().then(({ data }) => setHero(data));
  }, []);

  return (
    <>
      <SEO
        title="Home"
        description="UNTOLD — The Story Behind The Glory. Premium global sports storytelling — documentaries, live scores, and fan community."
        path="/"
      />
      <HeroBanner content={hero} />
      <LiveNow />
      <Trending />
      <CategoryRow
        category="shorts"
        title={t('home.shorts')}
        subtitle={t('home.shortsSubtitle')}
        viewAllLink="/shorts"
        variant="short"
      />
      <BreakingNews />
      <CategoryRow
        category="legends"
        title={t('home.legends')}
        subtitle={t('home.legendsSubtitle')}
        viewAllLink="/legends"
      />
      <RivalriesRow />
      <CategoryRow
        category="stories"
        title={t('home.stories')}
        subtitle={t('home.storiesSubtitle')}
        viewAllLink="/stories"
      />
      <CategoryRow
        category="secrets"
        title={t('home.secrets')}
        subtitle={t('home.secretsSubtitle')}
        viewAllLink="/secrets"
      />
      <FanWarsRow />
      <MembershipCTA />
      <PlatformFeatures />
    </>
  );
}
