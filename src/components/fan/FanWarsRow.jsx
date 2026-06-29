import { useState } from 'react';
import { Link } from 'react-router-dom';
import SectionHeader from '../ui/SectionHeader';
import Badge from '../ui/Badge';
import SectionReveal from '../ui/SectionReveal';
import { communityApi } from '../../api/community';
import { FAN_WARS } from '../../data/fanCatalog';

function ShareButton({ title }) {
  const handleShare = async () => {
    const url = window.location.origin + '/fan-wars';
    if (navigator.share) {
      await navigator.share({ title: `UNTOLD Fan Wars: ${title}`, url });
    } else {
      await navigator.clipboard.writeText(url);
    }
  };

  return (
    <button
      type="button"
      onClick={handleShare}
      className="text-xs font-semibold text-untold-gold hover:text-untold-gold-light transition-colors"
    >
      Share
    </button>
  );
}

export default function FanWarsRow({ wars: initialWars = FAN_WARS }) {
  const [wars, setWars] = useState(initialWars.slice(0, 3));

  const handleVote = async (warId, side) => {
    await communityApi.voteFanWar(warId, side);
    setWars((prev) =>
      prev.map((w) => {
        if (w.id !== warId) return w;
        const key = side === 'a' ? 'teamA' : 'teamB';
        return { ...w, [key]: { ...w[key], votes: w[key].votes + 1 } };
      })
    );
  };

  return (
    <SectionReveal className="py-12 sm:py-16 dark:bg-untold-surface/30 light:bg-gray-50/50" aria-labelledby="fan-wars">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <SectionHeader title="Fan Wars" subtitle="Pick your side — live community votes" viewAllLink="/fan-wars" />
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-5">
          {wars.map((war) => {
            const total = war.teamA.votes + war.teamB.votes;
            const pctA = Math.round((war.teamA.votes / total) * 100);
            const pctB = 100 - pctA;
            return (
              <article
                key={war.id}
                className="rounded-xl border dark:border-untold-border light:border-gray-200 dark:bg-untold-surface light:bg-white p-5 card-premium glass-card"
              >
                <div className="flex items-center justify-between mb-4">
                  <Badge variant="gold" size="sm">{war.sport}</Badge>
                  <div className="flex items-center gap-3">
                    {war.status === 'live' && <Badge variant="live" pulse size="sm">Live</Badge>}
                    <ShareButton title={war.title} />
                  </div>
                </div>
                <h3 className="font-display text-lg font-bold dark:text-untold-white light:text-black">{war.title}</h3>
                <div className="mt-4 flex h-2.5 rounded-full overflow-hidden dark:bg-white/10 light:bg-gray-200">
                  <div className="bg-untold-gold transition-all duration-500" style={{ width: `${pctA}%` }} />
                  <div className="bg-white/25 transition-all duration-500" style={{ width: `${pctB}%` }} />
                </div>
                <div className="mt-4 grid grid-cols-2 gap-2">
                  <button
                    type="button"
                    onClick={() => handleVote(war.id, 'a')}
                    className="py-3 rounded-xl text-sm font-bold border dark:border-white/10 light:border-gray-200
                      hover:border-untold-gold hover:bg-untold-gold/10 hover:text-untold-gold transition-all"
                  >
                    {war.teamA.name}
                    <span className="block text-xs font-semibold text-untold-gold mt-0.5">{pctA}%</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => handleVote(war.id, 'b')}
                    className="py-3 rounded-xl text-sm font-bold border dark:border-white/10 light:border-gray-200
                      hover:border-untold-gold hover:bg-untold-gold/10 hover:text-untold-gold transition-all"
                  >
                    {war.teamB.name}
                    <span className="block text-xs font-semibold text-untold-gold mt-0.5">{pctB}%</span>
                  </button>
                </div>
              </article>
            );
          })}
        </div>
      </div>
    </SectionReveal>
  );
}
