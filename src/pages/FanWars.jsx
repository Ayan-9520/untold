import { useEffect, useState } from 'react';
import SEO from '../components/SEO';
import SectionHeader from '../components/ui/SectionHeader';
import Badge from '../components/ui/Badge';
import { communityApi } from '../api/community';

export default function FanWarsPage() {
  const [wars, setWars] = useState([]);

  useEffect(() => {
    communityApi.getFanWars().then(setWars).catch(() => setWars([]));
  }, []);

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
    <>
      <SEO title="Fan Wars" description="Community sports battles on UNTOLD" path="/fan-wars" />
      <section className="pt-28 pb-4">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 text-center mb-4">
          <h1 className="font-display text-3xl sm:text-4xl font-bold dark:text-untold-white light:text-black">Fan Wars</h1>
          <p className="mt-2 text-sm dark:text-untold-muted light:text-gray-600">Pick your side. Rally your tribe.</p>
        </div>
      </section>
      <section className="pb-16">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <SectionHeader title="All Fan Wars" subtitle="Live community votes" />
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-5">
            {wars.map((war) => {
              const total = war.teamA.votes + war.teamB.votes;
              const pctA = total > 0 ? Math.round((war.teamA.votes / total) * 100) : 50;
              const pctB = 100 - pctA;
              return (
                <article key={war.id} className="rounded-xl border dark:border-untold-border light:border-gray-200 dark:bg-untold-surface light:bg-white p-5">
                  <Badge variant="gold" size="sm">{war.sport}</Badge>
                  <h3 className="font-display text-lg font-bold dark:text-untold-white light:text-black mt-3">{war.title}</h3>
                  <div className="mt-4 grid grid-cols-2 gap-2">
                    <button type="button" onClick={() => handleVote(war.id, 'a')} className="py-3 rounded-xl text-sm font-bold border dark:border-white/10 light:border-gray-200 hover:border-untold-gold">
                      {war.teamA.name} · {pctA}%
                    </button>
                    <button type="button" onClick={() => handleVote(war.id, 'b')} className="py-3 rounded-xl text-sm font-bold border dark:border-white/10 light:border-gray-200 hover:border-untold-gold">
                      {war.teamB.name} · {pctB}%
                    </button>
                  </div>
                </article>
              );
            })}
          </div>
        </div>
      </section>
    </>
  );
}
