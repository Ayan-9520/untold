import { Link } from 'react-router-dom';
import SectionHeader from '../ui/SectionHeader';
import Badge from '../ui/Badge';
import { PREDICTION_EVENTS, PREDICTION_LEADERBOARD } from '../../data/fanCatalog';

export default function PredictionLeagueRow() {
  return (
    <section className="py-12 sm:py-16" aria-labelledby="prediction-league">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <SectionHeader title="Prediction League" subtitle="Predict winners, earn coins & badges" viewAllLink="/predictions" />
        <div className="grid lg:grid-cols-3 gap-5">
          <div className="lg:col-span-2 grid sm:grid-cols-2 gap-4">
            {PREDICTION_EVENTS.map((event) => (
              <Link
                key={event.id}
                to="/predictions"
                className="rounded-xl border dark:border-untold-border light:border-gray-200 dark:bg-untold-surface light:bg-white p-5 card-premium group"
              >
                <Badge variant="outline" size="sm">{event.sport}</Badge>
                <h3 className="font-display text-lg font-bold dark:text-untold-white light:text-black mt-2 group-hover:text-untold-gold transition-colors">
                  {event.title}
                </h3>
                <p className="text-sm dark:text-untold-muted light:text-gray-500 mt-1">
                  Pool: {event.pool.toLocaleString()} coins
                </p>
                <div className="mt-3 flex flex-wrap gap-2">
                  <Badge variant="gold" size="sm">+{event.rewards.coins} coins</Badge>
                  {event.rewards.badge && <Badge variant="muted" size="sm">{event.rewards.badge}</Badge>}
                </div>
              </Link>
            ))}
          </div>
          <div className="rounded-xl border dark:border-untold-border light:border-gray-200 dark:bg-untold-surface light:bg-white p-5">
            <h3 className="font-display font-bold dark:text-untold-white light:text-black mb-4">Leaderboard</h3>
            <ol className="space-y-3">
              {PREDICTION_LEADERBOARD.slice(0, 5).map((entry) => (
                <li
                  key={entry.rank}
                  className={`flex items-center justify-between text-sm ${entry.isUser ? 'text-untold-gold font-semibold' : 'dark:text-untold-muted light:text-gray-600'}`}
                >
                  <span>#{entry.rank} {entry.name}</span>
                  <span className="tabular-nums">{entry.points} pts</span>
                </li>
              ))}
            </ol>
            <Link to="/predictions" className="block mt-4 text-sm text-untold-gold font-semibold hover:underline">
              Full leaderboard →
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}
