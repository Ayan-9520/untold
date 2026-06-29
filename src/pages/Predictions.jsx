import SEO from '../components/SEO';
import PredictionLeagueRow from '../components/fan/PredictionLeagueRow';

export default function PredictionsPage() {
  return (
    <>
      <SEO title="Prediction League" description="Predict match outcomes and climb the leaderboard" path="/predictions" />
      <section className="pt-28 pb-4">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 text-center mb-4">
          <h1 className="font-display text-3xl sm:text-4xl font-bold dark:text-untold-white light:text-black">Prediction League</h1>
          <p className="mt-2 text-sm dark:text-untold-muted light:text-gray-600">Earn coins, badges, and premium unlocks.</p>
        </div>
      </section>
      <PredictionLeagueRow />
    </>
  );
}
