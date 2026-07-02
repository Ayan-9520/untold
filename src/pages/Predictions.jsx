import { useEffect, useState } from 'react';
import SEO from '../components/SEO';
import Badge from '../components/ui/Badge';
import { communityApi } from '../api/community';

export default function PredictionsPage() {
  const [events, setEvents] = useState([]);
  const [leaderboard, setLeaderboard] = useState([]);

  useEffect(() => {
    communityApi.getPredictions()
      .then(({ events: ev, leaderboard: lb }) => {
        setEvents(ev);
        setLeaderboard(lb);
      })
      .catch(() => {
        setEvents([]);
        setLeaderboard([]);
      });
  }, []);

  return (
    <>
      <SEO title="Prediction League" description="Predict match outcomes and climb the leaderboard" path="/predictions" />
      <section className="pt-28 pb-4">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 text-center mb-4">
          <h1 className="font-display text-3xl sm:text-4xl font-bold dark:text-untold-white light:text-black">Prediction League</h1>
          <p className="mt-2 text-sm dark:text-untold-muted light:text-gray-600">Earn coins, badges, and premium unlocks.</p>
        </div>
      </section>
      <section className="pb-16">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 grid lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-4">
            {events.map((event) => (
              <article key={event.id} className="rounded-xl border dark:border-untold-border light:border-gray-200 p-5 dark:bg-untold-surface light:bg-white">
                <Badge variant="outline" size="sm">{event.sport}</Badge>
                <h2 className="font-display text-xl font-bold dark:text-untold-white light:text-black mt-2">{event.title}</h2>
                <p className="text-sm dark:text-untold-muted light:text-gray-500 mt-1">Pool: {(event.pool || 0).toLocaleString()} coins</p>
              </article>
            ))}
          </div>
          <div className="rounded-xl border dark:border-untold-border light:border-gray-200 p-5 dark:bg-untold-surface light:bg-white">
            <h2 className="font-display font-bold dark:text-untold-white light:text-black mb-4">Leaderboard</h2>
            <ol className="space-y-3">
              {leaderboard.map((entry) => (
                <li key={entry.rank} className={`flex justify-between text-sm ${entry.isUser ? 'text-untold-gold font-semibold' : 'dark:text-untold-muted light:text-gray-600'}`}>
                  <span>#{entry.rank} {entry.name}</span>
                  <span>{entry.points} pts</span>
                </li>
              ))}
            </ol>
          </div>
        </div>
      </section>
    </>
  );
}
