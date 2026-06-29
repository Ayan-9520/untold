import { useState } from 'react';
import SectionHeader from '../ui/SectionHeader';
import Badge from '../ui/Badge';
import { DEBATE_ARENAS } from '../../data/fanCatalog';
import { communityApi } from '../../api/community';

export default function DebateArenaRow() {
  const [debates, setDebates] = useState(DEBATE_ARENAS);

  const vote = async (debateId, optionId) => {
    setDebates((prev) =>
      prev.map((d) => {
        if (d.id !== debateId) return d;
        const isA = d.optionA.id === optionId;
        return {
          ...d,
          optionA: { ...d.optionA, votes: d.optionA.votes + (isA ? 1 : 0) },
          optionB: { ...d.optionB, votes: d.optionB.votes + (isA ? 0 : 1) },
        };
      })
    );
    try {
      await communityApi.voteFanWar(debateId, optionId);
    } catch { /* local update kept */ }
  };

  return (
    <section className="py-12 sm:py-16 dark:bg-untold-surface/30 light:bg-gray-50/50">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <SectionHeader title="AI Debate Arena" subtitle="GOAT debates — cast your vote" />
        <div className="grid md:grid-cols-2 gap-5">
          {debates.map((debate) => {
            const total = debate.optionA.votes + debate.optionB.votes;
            const pctA = Math.round((debate.optionA.votes / total) * 100);
            return (
              <article key={debate.id} className="relative rounded-xl overflow-hidden border dark:border-untold-border light:border-gray-200 min-h-[220px]">
                <img src={debate.image} alt="" className="absolute inset-0 w-full h-full object-cover" />
                <div className="absolute inset-0 bg-gradient-to-t from-black via-black/70 to-black/30" />
                <div className="relative p-5 sm:p-6 flex flex-col h-full justify-end">
                  <Badge variant="gold" size="sm" className="self-start mb-2">{debate.sport}</Badge>
                  <h3 className="font-display text-2xl font-bold text-white">{debate.title}</h3>
                  <div className="mt-4 grid grid-cols-2 gap-2">
                    <button
                      type="button"
                      onClick={() => vote(debate.id, debate.optionA.id)}
                      className="py-2.5 rounded-lg bg-untold-gold/90 text-untold-dark text-sm font-bold hover:bg-untold-gold transition-colors"
                    >
                      {debate.optionA.label} · {pctA}%
                    </button>
                    <button
                      type="button"
                      onClick={() => vote(debate.id, debate.optionB.id)}
                      className="py-2.5 rounded-lg bg-white/15 text-white text-sm font-bold hover:bg-white/25 transition-colors backdrop-blur-sm"
                    >
                      {debate.optionB.label} · {100 - pctA}%
                    </button>
                  </div>
                </div>
              </article>
            );
          })}
        </div>
      </div>
    </section>
  );
}
