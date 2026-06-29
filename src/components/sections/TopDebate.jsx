import { debates, polls, getFeaturedDebate } from '../../data/engagementData';
import SectionHeader from '../ui/SectionHeader';
import ContentRow from '../ui/ContentRow';
import DebateCard from '../engagement/DebateCard';
import PollCard from '../engagement/PollCard';

export default function TopDebate() {
  const featured = getFeaturedDebate();
  const sidePolls = polls.slice(0, 3);

  return (
    <section className="py-10 sm:py-14" aria-labelledby="top-debate">
      <SectionHeader
        title="Today's Top Debate"
        subtitle="Cast your vote — join the conversation"
      />
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 lg:gap-8">
          <DebateCard debate={featured} />
          <div className="space-y-4">
            <p className="text-sm font-semibold uppercase tracking-wider dark:text-untold-muted light:text-gray-500">
              More debates
            </p>
            {debates.filter((d) => d.id !== featured.id).map((d) => (
              <DebateCard key={d.id} debate={d} compact />
            ))}
          </div>
        </div>

        <div className="mt-10">
          <h3 className="font-display text-lg font-bold dark:text-untold-white light:text-black mb-4 px-0">
            Quick Polls
          </h3>
          <ContentRow>
            {sidePolls.map((poll) => (
              <PollCard key={poll.id} poll={poll} />
            ))}
          </ContentRow>
        </div>
      </div>
    </section>
  );
}
