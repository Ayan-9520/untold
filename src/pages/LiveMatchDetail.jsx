import { useEffect, useState } from 'react';
import { useParams, Link, Navigate } from 'react-router-dom';
import SEO from '../components/SEO';
import Badge from '../components/ui/Badge';
import Loader from '../components/ui/Loader';
import AICommentaryFeed from '../components/live/AICommentaryFeed';
import EventUpdateFeed from '../components/live/EventUpdateFeed';
import MatchTimeline from '../components/live/MatchTimeline';
import LiveHighlights from '../components/live/LiveHighlights';
import LiveMatchPoll from '../components/live/LiveMatchPoll';
import liveApi from '../api/live';

export default function LiveMatchDetail() {
  const { id } = useParams();
  const [match, setMatch] = useState(null);
  const [commentary, setCommentary] = useState([]);
  const [updates, setUpdates] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;

    async function load() {
      const [matchRes, commRes, eventsRes] = await Promise.all([
        liveApi.getMatch(id),
        liveApi.getCommentary(id),
        liveApi.getEvents(id),
      ]);
      if (!active) return;
      setMatch(matchRes.data);
      setCommentary(commRes.data);
      setUpdates(
        (eventsRes.data || []).map((u, i) => ({
          ...u,
          id: u.id || `${id}-u${i}`,
          matchId: id,
          eventName: matchRes.data?.eventName,
          sport: matchRes.data?.sport,
          aiText: u.raw || u.aiText,
        }))
      );
      setLoading(false);
    }

    load();

    const disconnect = liveApi.connectLive((msg) => {
      if (msg.type === 'live_update' && msg.data?.match_id === id) {
        load();
      }
    });

    return () => {
      active = false;
      disconnect();
    };
  }, [id]);

  if (loading) return <Loader fullScreen label="Loading match" />;
  if (!match) return <Navigate to="/live" replace />;

  const [teamA, teamB] = match.teamsOrPlayers || [];
  const score = match.score || {};

  return (
    <>
      <SEO
        title={match.eventName}
        description={`Live scores and AI commentary — ${match.eventName}`}
        path={`/live/${match.id}`}
      />

      <section className="relative pt-24 sm:pt-28 pb-8">
        <div className="absolute inset-0 h-[420px] sm:h-[480px]">
          <img src={match.thumbnail} alt="" className="h-full w-full object-cover" />
          <div className="absolute inset-0 hero-gradient" />
        </div>

        <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <Link to="/live" className="text-sm text-untold-gold hover:underline mb-4 inline-block">
            ← All Live Matches
          </Link>

          <div className="flex flex-wrap gap-2 mb-4">
            <Badge variant="live" pulse>Live</Badge>
            <Badge variant="muted" size="sm">{match.sport}</Badge>
            {match.league && <Badge variant="outline" size="sm">{match.league}</Badge>}
          </div>

          <h1 className="font-display text-3xl sm:text-4xl lg:text-5xl font-bold text-white max-w-4xl">
            {match.eventName}
          </h1>

          {match.location && (
            <p className="mt-2 text-sm text-white/70">{match.location}</p>
          )}

          <div className="mt-8 grid sm:grid-cols-3 gap-6 max-w-2xl">
            <div className="rounded-xl bg-black/40 backdrop-blur-sm border border-white/10 p-4">
              <p className="text-xs text-white/60 uppercase tracking-wider">{teamA}</p>
              {teamB && <p className="text-xs text-white/60 uppercase tracking-wider mt-2">{teamB}</p>}
            </div>
            <div className="rounded-xl bg-black/40 backdrop-blur-sm border border-untold-gold/30 p-4 text-center">
              <p className="text-3xl sm:text-4xl font-bold text-gold-gradient">{score.display}</p>
              <p className="text-xs text-untold-gold-light mt-1 uppercase tracking-wider">Score</p>
            </div>
            <div className="rounded-xl bg-black/40 backdrop-blur-sm border border-white/10 p-4">
              <p className="text-xs text-white/60 uppercase tracking-wider">Status</p>
              <p className="text-lg font-semibold text-white mt-1">{match.timer}</p>
              <p className="text-xs text-red-400 mt-1 capitalize">{match.status}</p>
            </div>
          </div>
        </div>
      </section>

      <section className="py-8 sm:py-12">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 grid lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-8">
            <AICommentaryFeed commentary={commentary} />
            <EventUpdateFeed updates={updates} title="Match Updates" showMatchLink={false} />
          </div>
          <div className="space-y-8">
            <MatchTimeline timeline={match.timeline} />
            <LiveMatchPoll prediction={match.predictions} />
          </div>
        </div>
      </section>

      {match.highlights?.length > 0 && (
        <LiveHighlights
          highlights={match.highlights.map((h) => ({ ...h, matchId: match.id, eventName: match.eventName }))}
          title="Match Highlights"
          subtitle="Key moments from this match"
        />
      )}
    </>
  );
}
