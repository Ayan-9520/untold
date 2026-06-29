import { useNavigate } from 'react-router-dom';
import { PlayIcon, PlusIcon, InfoIcon } from '../../components/icons';
import { useWatchlist } from '../context/WatchlistContext';

export default function MobileHero({ content }) {
  const navigate = useNavigate();
  const { isInWatchlist, toggleWatchlist } = useWatchlist();

  if (!content) {
    return <div className="h-[52dvh] skeleton" />;
  }

  const inList = isInWatchlist(content.id);

  return (
    <section className="relative h-[52dvh] min-h-[380px] w-full overflow-hidden">
      <img
        src={content.heroImage || content.image}
        alt=""
        className="absolute inset-0 w-full h-full object-cover"
      />
      <div className="absolute inset-0 bg-gradient-to-t from-untold-dark via-untold-dark/40 to-transparent" />
      <div className="absolute inset-0 bg-gradient-to-r from-untold-dark/60 to-transparent" />

      <div className="absolute bottom-0 left-0 right-0 p-4 pb-6">
        <span className="inline-block px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-untold-gold text-untold-dark mb-2">
          Featured
        </span>

        <h2 className="font-display text-2xl font-bold text-white leading-tight line-clamp-2">
          {content.title}
        </h2>

        <div className="flex items-center gap-2 mt-1.5 text-xs text-white/70">
          <span>{content.category}</span>
          <span>·</span>
          <span>{content.duration}</span>
          <span>·</span>
          <span className="border border-white/30 px-1 rounded text-[10px]">{content.rating}</span>
        </div>

        <p className="text-xs text-white/60 mt-2 line-clamp-2 leading-relaxed">
          {content.description}
        </p>

        <div className="flex items-center gap-2 mt-4">
          <button
            onClick={() => navigate(`/app/watch/${content.id}`)}
            className="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg
              bg-untold-gold text-untold-dark font-semibold text-sm
              active:scale-[0.98] transition-transform"
          >
            <PlayIcon className="w-4 h-4" />
            Play
          </button>
          <button
            onClick={() => toggleWatchlist(content)}
            className="p-2.5 rounded-lg bg-white/15 backdrop-blur-sm text-white
              active:scale-[0.98] transition-transform"
            aria-label={inList ? 'Remove from list' : 'Add to list'}
          >
            {inList ? (
              <InfoIcon className="w-5 h-5 text-untold-gold" />
            ) : (
              <PlusIcon className="w-5 h-5" />
            )}
          </button>
        </div>
      </div>
    </section>
  );
}
