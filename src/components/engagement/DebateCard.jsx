import { useMemo } from 'react';
import { useEngagement } from '../../context/EngagementContext';

export default function DebateCard({ debate, compact = false }) {
  const { vote, getUserVote, getVoteCounts } = useEngagement();
  const userVote = getUserVote(debate.id, 'debate');
  const options = useMemo(() => getVoteCounts(debate, 'debate'), [debate, getVoteCounts, userVote]);

  const total = options.reduce((sum, o) => sum + o.votes, 0);

  const handleVote = (optionId) => {
    if (!userVote) vote(debate.id, optionId, 'debate');
  };

  return (
    <article
      className={`rounded-xl border dark:border-untold-border light:border-gray-200 overflow-hidden
        dark:bg-untold-surface light:bg-white card-hover
        ${compact ? 'p-4' : 'p-5 sm:p-6'}`}
    >
      {!compact && (
        <p className="text-xs font-semibold uppercase tracking-wider text-untold-gold mb-2">
          {debate.subtitle} · {debate.sport}
        </p>
      )}
      <h3 className={`font-display font-bold dark:text-untold-white light:text-black ${compact ? 'text-base mb-3' : 'text-xl sm:text-2xl mb-4'}`}>
        {debate.question}
      </h3>

      <div className={`space-y-2 ${compact ? '' : 'space-y-3'}`}>
        {options.map((opt) => {
          const pct = total > 0 ? Math.round((opt.votes / total) * 100) : 0;
          const isSelected = userVote === opt.id;
          const showResults = !!userVote;

          return (
            <button
              key={opt.id}
              type="button"
              onClick={() => handleVote(opt.id)}
              disabled={!!userVote}
              className={`relative w-full text-left rounded-lg overflow-hidden transition-all
                ${userVote ? 'cursor-default' : 'cursor-pointer hover:ring-2 hover:ring-untold-gold/50'}
                ${isSelected ? 'ring-2 ring-untold-gold' : ''}
                dark:bg-white/5 light:bg-gray-50 border dark:border-white/10 light:border-gray-100`}
            >
              {showResults && (
                <div
                  className="absolute inset-y-0 left-0 bg-untold-gold/20 transition-all duration-700"
                  style={{ width: `${pct}%` }}
                />
              )}
              <div className="relative flex items-center justify-between px-4 py-3">
                <span className={`font-medium ${isSelected ? 'text-untold-gold' : 'dark:text-untold-white light:text-black'}`}>
                  {opt.label}
                </span>
                {showResults && (
                  <span className="text-sm font-semibold dark:text-untold-muted light:text-gray-500 tabular-nums">
                    {pct}%
                  </span>
                )}
              </div>
            </button>
          );
        })}
      </div>

      <p className="mt-3 text-xs dark:text-untold-muted light:text-gray-500">
        {total.toLocaleString()} votes
        {userVote ? ' · Thanks for voting!' : ' · Tap to cast your vote'}
      </p>
    </article>
  );
}
