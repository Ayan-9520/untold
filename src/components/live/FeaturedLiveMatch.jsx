import { Link } from 'react-router-dom';
import Button from '../ui/Button';
import Badge from '../ui/Badge';
import { PlayIcon } from '../icons';

export default function FeaturedLiveMatch({ match }) {
  if (!match) return null;

  const [teamA, teamB] = match.teamsOrPlayers || [];
  const score = match.score || {};
  const latest = match.commentary?.[0];

  return (
    <section className="relative overflow-hidden rounded-2xl mx-4 sm:mx-6 lg:mx-8 max-w-7xl lg:mx-auto">
      <div className="relative aspect-[16/9] sm:aspect-[21/9] min-h-[320px] sm:min-h-[380px] rounded-2xl overflow-hidden">
        <img src={match.thumbnail} alt="" className="absolute inset-0 h-full w-full object-cover" />
        <div className="absolute inset-0 hero-gradient" />

        <div className="absolute inset-0 flex flex-col justify-end p-6 sm:p-10 lg:p-12">
          <div className="flex flex-wrap items-center gap-2 mb-4">
            <Badge variant="live" pulse>Live</Badge>
            <Badge variant="muted" size="sm">{match.sport}</Badge>
            {match.league && <Badge variant="outline" size="sm">{match.league}</Badge>}
          </div>

          <h1 className="font-display text-2xl sm:text-4xl lg:text-5xl font-bold text-white max-w-3xl leading-tight">
            {match.eventName}
          </h1>

          <div className="mt-4 flex flex-wrap items-end gap-6 sm:gap-10">
            <div>
              <p className="text-sm text-white/70 uppercase tracking-wider">{teamA}</p>
              {teamB && <p className="text-sm text-white/70 uppercase tracking-wider mt-1">{teamB}</p>}
            </div>
            <p className="font-display text-4xl sm:text-5xl font-bold text-gold-gradient">
              {score.display}
            </p>
            <div>
              <p className="text-xs text-untold-gold-light uppercase tracking-widest font-semibold">Match Status</p>
              <p className="text-lg font-semibold text-white mt-0.5">{match.timer}</p>
            </div>
          </div>

          {latest && (
            <p className="mt-4 text-sm sm:text-base text-white/85 max-w-2xl line-clamp-2">
              <span className="text-untold-gold font-semibold">AI: </span>{latest.text}
            </p>
          )}

          <div className="mt-6 flex flex-wrap gap-3">
            <Link to={`/live/${match.id}`}>
              <Button size="lg" icon={<PlayIcon className="w-4 h-4" />}>
                Follow Live
              </Button>
            </Link>
            <Link to={`/live/${match.id}#commentary`}>
              <Button variant="outline" size="lg" className="border-white/30 text-white hover:bg-white/10">
                AI Commentary
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}
