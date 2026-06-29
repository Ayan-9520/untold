import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import SectionHeader from '../ui/SectionHeader';
import ContentRow from '../ui/ContentRow';
import LiveScoreCard from '../live/LiveScoreCard';
import SectionReveal from '../ui/SectionReveal';
import liveApi from '../../api/live';

export default function LiveNow() {
  const [matches, setMatches] = useState([]);

  useEffect(() => {
    liveApi.getOverview().then(({ matches: m }) => {
      setMatches(m.slice(0, 8));
    });

    const disconnect = liveApi.connectLive((msg) => {
      if (msg.type === 'live_update') {
        liveApi.getOverview().then(({ matches: m }) => setMatches(m.slice(0, 8)));
      }
    });
    return disconnect;
  }, []);

  if (matches.length === 0) return null;

  return (
    <SectionReveal className="py-10 sm:py-14 border-b dark:border-untold-border/40 light:border-gray-200" aria-labelledby="live-now">
      <div className="flex items-center gap-2 px-4 sm:px-6 lg:px-8 mb-1">
        <span className="relative flex h-2.5 w-2.5">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-500 opacity-75" />
          <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-red-500" />
        </span>
        <span className="text-sm sm:text-base font-bold uppercase tracking-wider text-white dark:text-untold-white light:text-black">
          LIVE NOW <span className="text-red-500">🔴</span>
        </span>
      </div>
      <SectionHeader
        title="Live Scores"
        subtitle="Real-time match updates — cricket, football, tennis & more"
        viewAllLink="/live"
      />

      <ContentRow>
        {matches.map((m) => (
          <LiveScoreCard key={m.id} match={m} />
        ))}
      </ContentRow>

      <div className="text-center mt-6 px-4">
        <Link to="/live" className="text-sm font-semibold text-untold-gold hover:underline">
          View all live matches →
        </Link>
      </div>
    </SectionReveal>
  );
}
