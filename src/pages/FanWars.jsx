import SEO from '../components/SEO';
import FanWarsRow from '../components/fan/FanWarsRow';
import { FAN_WARS } from '../data/fanCatalog';

export default function FanWarsPage() {
  return (
    <>
      <SEO title="Fan Wars" description="Community sports battles on UNTOLD" path="/fan-wars" />
      <section className="pt-28 pb-4">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 text-center mb-4">
          <h1 className="font-display text-3xl sm:text-4xl font-bold dark:text-untold-white light:text-black">Fan Wars</h1>
          <p className="mt-2 text-sm dark:text-untold-muted light:text-gray-600">Pick your side. Rally your tribe.</p>
        </div>
      </section>
      <FanWarsRow wars={FAN_WARS} />
    </>
  );
}
