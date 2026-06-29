import { Link } from 'react-router-dom';
import SectionHeader from '../ui/SectionHeader';
import ContentRow from '../ui/ContentRow';
import Badge from '../ui/Badge';

export default function LiveHighlights({ highlights = [], title = 'Live Highlights', subtitle }) {
  if (highlights.length === 0) return null;

  return (
    <section className="py-10 sm:py-12">
      <SectionHeader title={title} subtitle={subtitle || 'Goals, wickets, knockouts & key moments'} viewAllLink="/live" />
      <ContentRow>
        {highlights.map((h) => (
          <Link
            key={h.id}
            to={`/live/${h.matchId}`}
            className="shrink-0 w-[200px] sm:w-[220px] group card-premium"
          >
            <div className="relative aspect-video rounded-xl overflow-hidden">
              <img src={h.thumbnail} alt="" className="h-full w-full object-cover group-hover:scale-105 transition-transform duration-500" loading="lazy" />
              <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent" />
              <Badge variant="muted" size="sm" className="absolute top-2 left-2">{h.type}</Badge>
              <span className="absolute bottom-2 right-2 text-[10px] font-bold text-white bg-black/60 px-1.5 py-0.5 rounded">
                {h.minute}
              </span>
            </div>
            <p className="mt-2 text-sm font-semibold dark:text-untold-white light:text-black line-clamp-2 group-hover:text-untold-gold transition-colors">
              {h.title}
            </p>
            <p className="text-[10px] dark:text-untold-muted light:text-gray-500 mt-0.5 line-clamp-1">{h.eventName}</p>
          </Link>
        ))}
      </ContentRow>
    </section>
  );
}
