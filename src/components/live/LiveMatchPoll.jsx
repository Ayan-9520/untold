import { useState } from 'react';
import Chip from '../ui/Chip';

/**
 * Phase 2 — Fan prediction / poll on live match detail
 */
export default function LiveMatchPoll({ prediction }) {
  const [voted, setVoted] = useState(null);
  const [votes, setVotes] = useState(
    prediction?.options?.reduce((acc, o) => ({ ...acc, [o.id]: o.votes }), {}) || {}
  );

  if (!prediction) return null;

  const total = Object.values(votes).reduce((a, b) => a + b, 0) || 1;

  const handleVote = (id) => {
    if (voted) return;
    setVoted(id);
    setVotes((prev) => ({ ...prev, [id]: (prev[id] || 0) + 1 }));
  };

  return (
    <div className="rounded-xl border border-untold-gold/30 dark:bg-untold-gold/5 light:bg-untold-gold/10 p-5">
      <p className="text-xs font-bold uppercase tracking-wider text-untold-gold mb-2">Fan Poll</p>
      <h3 className="font-display text-lg font-bold dark:text-untold-white light:text-black mb-4">
        {prediction.question}
      </h3>
      <div className="space-y-2">
        {prediction.options.map((opt) => {
          const pct = Math.round(((votes[opt.id] || 0) / total) * 100);
          return (
            <button
              key={opt.id}
              type="button"
              onClick={() => handleVote(opt.id)}
              disabled={!!voted}
              className={`w-full relative overflow-hidden rounded-lg px-4 py-3 text-left transition-all
                ${voted === opt.id ? 'ring-2 ring-untold-gold' : 'dark:bg-white/5 light:bg-white hover:ring-1 hover:ring-untold-gold/50'}
                ${voted ? 'cursor-default' : 'cursor-pointer'}`}
            >
              {voted && (
                <div
                  className="absolute inset-y-0 left-0 bg-untold-gold/20 transition-all duration-500"
                  style={{ width: `${pct}%` }}
                />
              )}
              <span className="relative flex justify-between text-sm font-medium dark:text-untold-white light:text-black">
                {opt.label}
                {voted && <span className="text-untold-gold">{pct}%</span>}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
