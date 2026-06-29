import { useNavigate } from 'react-router-dom';
import { PlayIcon } from '../../components/icons';
import { useWatchlist } from '../context/WatchlistContext';
import { BookmarkIcon } from '../../components/icons';

export default function MobileVideoCard({ item, variant = 'landscape', index = 0 }) {
  const navigate = useNavigate();
  const { isInWatchlist, toggleWatchlist } = useWatchlist();
  const isShort = variant === 'short';
  const inList = isInWatchlist(item.id);

  const handlePlay = () => {
    if (isShort) navigate('/app/shorts', { state: { startIndex: index } });
    else navigate(`/app/watch/${item.id}`);
  };

  return (
    <article
      className={`shrink-0 group ${isShort ? 'w-[120px]' : 'w-[140px]'}`}
      onClick={handlePlay}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && handlePlay()}
    >
      <div
        className={`relative overflow-hidden rounded-lg
          ${isShort ? 'aspect-[9/14]' : 'aspect-[2/3]'}
          dark:bg-untold-surface light:bg-gray-100`}
      >
        <img
          src={item.image}
          alt={item.title}
          loading="lazy"
          className="h-full w-full object-cover transition-transform duration-500 group-active:scale-95"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent" />

        {!isShort && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              toggleWatchlist(item);
            }}
            className="absolute top-2 right-2 p-1.5 rounded-full bg-black/40 backdrop-blur-sm
              active:scale-90 transition-transform"
            aria-label={inList ? 'Remove from watchlist' : 'Add to watchlist'}
          >
            <BookmarkIcon
              className={`w-3.5 h-3.5 ${inList ? 'text-untold-gold' : 'text-white'}`}
              filled={inList}
            />
          </button>
        )}

        <div className="absolute bottom-0 left-0 right-0 p-2">
          {item.duration && (
            <span className="text-[10px] text-white/80 font-medium">{item.duration}</span>
          )}
        </div>

        <div className="absolute inset-0 flex items-center justify-center opacity-0 group-active:opacity-100 transition-opacity">
          <div className="w-10 h-10 rounded-full bg-untold-gold/90 flex items-center justify-center">
            <PlayIcon className="w-4 h-4 text-untold-dark ml-0.5" />
          </div>
        </div>
      </div>

      <p className="mt-1.5 text-xs font-medium dark:text-untold-white light:text-black line-clamp-2 leading-tight">
        {item.title}
      </p>
      {item.category && (
        <p className="text-[10px] dark:text-untold-muted light:text-gray-400 mt-0.5">{item.category}</p>
      )}
    </article>
  );
}

export function MobileVideoCardSkeleton({ variant = 'landscape' }) {
  const isShort = variant === 'short';
  return (
    <div className={`shrink-0 ${isShort ? 'w-[120px]' : 'w-[140px]'}`}>
      <div className={`rounded-lg skeleton ${isShort ? 'aspect-[9/14]' : 'aspect-[2/3]'}`} />
      <div className="mt-1.5 h-3 w-full rounded skeleton" />
    </div>
  );
}
