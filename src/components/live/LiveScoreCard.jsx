import { Link } from 'react-router-dom';
import Badge from '../ui/Badge';

export default function LiveScoreCard({ match, compact = false }) {
  const [teamA, teamB] = match.teamsOrPlayers || [];
  const score = match.score || {};

  const content = (
    <article
      className={`group rounded-xl overflow-hidden border card-premium
        dark:bg-untold-surface light:bg-white
        border-red-500/30 ring-1 ring-red-500/10
        ${compact ? 'w-full' : 'shrink-0 w-[280px] sm:w-[300px]'}`}
    >
      <div className={`relative overflow-hidden ${compact ? 'aspect-[16/7]' : 'aspect-video'}`}>
        <img src={match.thumbnail} alt="" className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105" loading="lazy" />
        <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/40 to-transparent" />
        <Badge variant="live" size="sm" pulse className="absolute top-3 left-3">Live</Badge>
        <span className="absolute top-3 right-3 text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-black/60 text-white">
          {match.sport}
        </span>
        <div className="absolute bottom-0 left-0 right-0 p-3 sm:p-4">
          <p className="text-[10px] text-untold-gold-light uppercase tracking-wider font-semibold">{match.timer}</p>
          <div className="mt-1 flex items-center justify-between gap-2">
            <div className="min-w-0 flex-1">
              <p className="text-sm font-semibold text-white truncate">{teamA}</p>
              {teamB && <p className="text-sm font-semibold text-white/80 truncate">{teamB}</p>}
            </div>
            <div className="text-right shrink-0">
              <p className="text-lg font-bold text-untold-gold">{score.display || score.home}</p>
            </div>
          </div>
        </div>
      </div>

      {!compact && (
        <div className="p-3">
          <h3 className="font-semibold text-sm line-clamp-1 dark:text-untold-white light:text-black group-hover:text-untold-gold transition-colors">
            {match.eventName}
          </h3>
          {match.league && (
            <p className="text-[10px] dark:text-untold-muted light:text-gray-500 mt-0.5">{match.league}</p>
          )}
        </div>
      )}
    </article>
  );

  return (
    <Link to={`/live/${match.id}`} className={compact ? 'block' : 'shrink-0'}>
      {content}
    </Link>
  );
}
