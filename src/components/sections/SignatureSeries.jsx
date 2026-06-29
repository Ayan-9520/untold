import { Link } from 'react-router-dom';
import { signatureSeries } from '../../data/engagementData';
import SectionHeader from '../ui/SectionHeader';
import ContentRow from '../ui/ContentRow';

export default function SignatureSeries() {
  return (
    <section className="py-10 sm:py-12 border-t dark:border-untold-border/50 light:border-gray-200" aria-labelledby="signature-series">
      <SectionHeader
        title="UNTOLD Signature Series"
        subtitle="Monday Rivalry · Wednesday Secrets · Friday Legends"
      />
      <ContentRow>
        {signatureSeries.map((series) => (
          <Link
            key={series.id}
            to={series.path}
            className="shrink-0 w-[240px] sm:w-[280px] group rounded-xl p-5 border dark:border-untold-border light:border-gray-200
              dark:bg-untold-surface light:bg-white card-hover"
          >
            <span className="text-[10px] font-bold uppercase tracking-wider text-untold-gold">
              {series.accent}
            </span>
            <h3 className="mt-2 font-display text-lg font-bold dark:text-untold-white light:text-black group-hover:text-untold-gold transition-colors">
              {series.title}
            </h3>
            <p className="mt-1 text-xs dark:text-untold-muted light:text-gray-500">{series.schedule}</p>
            <p className="mt-3 text-sm dark:text-untold-white/70 light:text-gray-600 line-clamp-2">
              {series.description}
            </p>
          </Link>
        ))}
      </ContentRow>
    </section>
  );
}
