import { useMemo } from 'react';
import { useEngagement } from '../../context/EngagementContext';

export default function PollCard({ poll }) {
  const { vote, getUserVote, getVoteCounts } = useEngagement();
  const userVote = getUserVote(poll.id, 'poll');
  const options = useMemo(() => getVoteCounts(poll, 'poll'), [poll, getVoteCounts, userVote]);

  const total = options.reduce((sum, o) => sum + o.votes, 0);

  return (
    <article className="shrink-0 w-[260px] sm:w-[280px] rounded-xl p-4 border dark:border-untold-border light:border-gray-200 dark:bg-untold-surface light:bg-white card-hover">
      <h4 className="font-display text-base font-bold dark:text-untold-white light:text-black line-clamp-2 mb-3">
        {poll.question}
      </h4>
      <div className="space-y-2">
        {options.map((opt) => {
          const pct = total > 0 ? Math.round((opt.votes / total) * 100) : 0;
          const isSelected = userVote === opt.id;

          return (
            <button
              key={opt.id}
              type="button"
              onClick={() => !userVote && vote(poll.id, opt.id, 'poll')}
              disabled={!!userVote}
              className={`relative w-full text-left rounded-md overflow-hidden text-sm
                ${userVote ? '' : 'hover:ring-1 hover:ring-untold-gold/40'}
                ${isSelected ? 'ring-1 ring-untold-gold' : ''}
                dark:bg-white/5 light:bg-gray-50`}
            >
              {userVote && (
                <div className="absolute inset-y-0 left-0 bg-untold-gold/15" style={{ width: `${pct}%` }} />
              )}
              <div className="relative flex justify-between px-3 py-2">
                <span className={isSelected ? 'text-untold-gold font-medium' : 'dark:text-untold-white/90 light:text-gray-700'}>
                  {opt.label}
                </span>
                {userVote && <span className="text-xs tabular-nums dark:text-untold-muted">{pct}%</span>}
              </div>
            </button>
          );
        })}
      </div>
    </article>
  );
}
