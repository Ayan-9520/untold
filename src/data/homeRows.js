/**
 * Netflix-style homepage rows — curated order for UNTOLD ORIGINALS
 * Titles use i18n keys resolved in HomeRow via useTranslation()
 */
export const HOME_FEATURED_ROWS = [
  { type: 'trending', titleKey: 'home.trending', subtitleKey: 'home.trendingSubtitle', viewAll: '/originals' },
  { type: 'top10', titleKey: 'rows.top10Title', subtitleKey: 'rows.top10Subtitle', viewAll: '/originals' },
  { type: 'latest', titleKey: 'home.originals', subtitleKey: 'home.originalsSubtitle', viewAll: '/originals' },
  { type: 'comingSoon', titleKey: 'rows.comingSoonTitle', subtitleKey: 'rows.comingSoonSubtitle', viewAll: '/events' },
  { type: 'continue', titleKey: 'home.continueWatching', subtitleKey: 'home.continueSubtitle' },

  { type: 'vertical', vertical: 'sports', titleKey: 'rows.sportsLegends', viewAll: '/legends' },
  { type: 'category', category: 'rivalries', titleKey: 'rows.greatestRivalries', viewAll: '/rivalries' },
  { type: 'vertical', vertical: 'ufc', titleKey: 'rows.combatUfc', viewAll: '/explore?vertical=ufc' },

  { type: 'vertical', vertical: 'business', titleKey: 'rows.businessStartups', viewAll: '/explore?vertical=business' },
  { type: 'vertical', vertical: 'influencers', titleKey: 'rows.creatorsInfluencers', viewAll: '/explore?vertical=influencers' },

  { type: 'vertical', vertical: 'hollywood', titleKey: 'rows.hollywood', viewAll: '/explore?vertical=hollywood' },
  { type: 'vertical', vertical: 'bollywood', titleKey: 'rows.bollywood', viewAll: '/explore?vertical=bollywood' },

  { type: 'vertical', vertical: 'technology', titleKey: 'rows.technologyAi', viewAll: '/explore?vertical=technology' },
  { type: 'vertical', vertical: 'science', titleKey: 'rows.scienceSpace', viewAll: '/explore?vertical=science' },
  { type: 'vertical', vertical: 'history', titleKey: 'rows.historyWars', viewAll: '/explore?vertical=history' },
  { type: 'vertical', vertical: 'politics', titleKey: 'rows.politicsLeaders', viewAll: '/explore?vertical=politics' },

  { type: 'award', titleKey: 'rows.awardWinning', subtitleKey: 'rows.awardSubtitle', viewAll: '/originals' },
  { type: 'editors', titleKey: 'rows.editorsChoice', subtitleKey: 'rows.editorsSubtitle', viewAll: '/originals' },

  { type: 'vertical', vertical: 'crime', titleKey: 'rows.crimeMystery', viewAll: '/explore?vertical=crime' },
  { type: 'category', category: 'secrets', titleKey: 'rows.secretsInvestigations', viewAll: '/secrets' },
  { type: 'category', category: 'shorts', titleKey: 'rows.shortsReels', viewAll: '/shorts', variant: 'short' },
  { type: 'category', category: 'originals', titleKey: 'rows.fullCollections', viewAll: '/originals' },
];
