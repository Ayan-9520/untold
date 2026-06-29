import { useState, useRef } from 'react';
import { PlayIcon, BookmarkIcon } from '../icons';
import { useWatchlist } from '../../context/WatchlistContext';
import Badge from './Badge';

function WatchlistButton({ videoId, title, image, category, duration }) {
  const { isInWatchlist, toggleWatchlist } = useWatchlist();
  const inList = isInWatchlist(videoId);
  return (
    <button
      type="button"
      onClick={(e) => {
        e.stopPropagation();
        e.preventDefault();
        toggleWatchlist({ id: videoId, title, image, category, duration });
      }}
      aria-label={inList ? 'Remove from watchlist' : 'Add to watchlist'}
      className="absolute top-2 right-2 z-10 p-1.5 rounded-full bg-black/50 text-white opacity-0 group-hover:opacity-100 transition-opacity hover:bg-untold-gold hover:text-untold-dark"
    >
      <BookmarkIcon className="w-4 h-4" filled={inList} />
    </button>
  );
}

export default function VideoCard({
  title,
  image,
  category,
  format,
  duration,
  description,
  year,
  variant = 'default',
  views,
  onClick,
  showDescription = false,
  trailerUrl,
  videoId,
  showWatchlist = true,
  rating,
  fluid = false,
  compact = false,
}) {
  const isShort = variant === 'short';
  const isLegend = variant === 'legend';
  const isRivalry = variant === 'rivalry';
  const [hover, setHover] = useState(false);
  const videoRef = useRef(null);

  const widthClass = fluid
    ? 'w-full'
    : isShort
      ? 'w-[165px] sm:w-[180px]'
      : 'w-[220px] sm:w-[260px] md:w-[280px]';

  const onEnter = () => {
    setHover(true);
    if (trailerUrl && videoRef.current) {
      videoRef.current.currentTime = 0;
      videoRef.current.play().catch(() => {});
    }
  };

  const onLeave = () => {
    setHover(false);
    videoRef.current?.pause();
  };

  return (
    <article
      onClick={onClick}
      onMouseEnter={onEnter}
      onMouseLeave={onLeave}
      className={`group relative shrink-0 cursor-pointer card-premium ${widthClass}
        ${fluid && !isShort ? 'rounded-xl overflow-hidden border dark:border-untold-border light:border-gray-200 dark:bg-untold-surface light:bg-white' : ''}
        ${fluid && isShort ? 'rounded-xl overflow-hidden border dark:border-untold-border/80 light:border-gray-200 dark:bg-untold-surface light:bg-white' : ''}`}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      onKeyDown={onClick ? (e) => e.key === 'Enter' && onClick?.() : undefined}
    >
      <div
        className={`relative overflow-hidden
          dark:bg-untold-surface light:bg-untold-surface-light
          ${fluid ? 'rounded-none' : 'rounded-lg'}
          ${isShort ? 'aspect-[9/16]' : 'aspect-video'}`}
      >
        <img
          src={image}
          alt={title}
          loading="lazy"
          className={`h-full w-full object-cover transition-all duration-500 group-hover:scale-105
            ${hover && trailerUrl ? 'opacity-0' : 'opacity-100'}`}
        />

        {trailerUrl && (
          <video
            ref={videoRef}
            src={trailerUrl}
            muted
            loop
            playsInline
            className={`absolute inset-0 h-full w-full object-cover transition-opacity duration-300
              ${hover ? 'opacity-100' : 'opacity-0 pointer-events-none'}`}
          />
        )}

        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent opacity-60 group-hover:opacity-80 transition-opacity" />

        {!isShort && (
          <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all duration-300 pointer-events-none">
            <div className={`flex items-center justify-center rounded-full bg-untold-gold text-untold-dark play-glow transform scale-75 group-hover:scale-100 transition-transform
              ${compact || fluid ? 'h-10 w-10' : 'h-12 w-12'}`}>
              <PlayIcon className={compact || fluid ? 'w-5 h-5 ml-0.5' : 'w-5 h-5 ml-0.5'} />
            </div>
          </div>
        )}

        {showWatchlist && videoId && (
          <WatchlistButton videoId={videoId} title={title} image={image} category={category} duration={duration} />
        )}

        {duration && (
          <span className={`absolute bottom-2 right-2 rounded font-medium bg-black/70 text-white backdrop-blur-sm
            ${compact || fluid ? 'px-1.5 py-0.5 text-[10px]' : 'px-1.5 py-0.5 text-xs'}`}>
            {duration}
          </span>
        )}
      </div>

      <div className={fluid ? (isShort ? 'p-3' : 'p-4') : `${compact ? 'mt-2' : 'mt-3'}`}>
        <h3
          className={`font-semibold leading-tight line-clamp-2
            dark:text-untold-white light:text-black
            group-hover:text-untold-gold transition-colors
            ${fluid && !isShort ? 'font-display text-base sm:text-lg' : ''}
            ${isShort ? (fluid ? 'text-sm sm:text-base' : 'text-xs sm:text-sm') : ''}
            ${!fluid && !isShort ? (compact ? 'text-sm' : 'text-base') : ''}`}
        >
          {title}
        </h3>

        {description && (isLegend || isRivalry || showDescription) && (
          <p className={`mt-1.5 dark:text-untold-muted light:text-gray-500 ${compact ? 'text-xs line-clamp-1' : 'text-sm line-clamp-2'}`}>
            {description}
          </p>
        )}

        {!isShort && (category || format || year || rating) && (
          <div className={`${fluid ? 'mt-3 pt-3' : 'mt-2 pt-2'} border-t dark:border-untold-border/60 light:border-gray-100 flex flex-wrap items-center gap-2`}>
            {category && <Badge variant="gold" size="sm">{category}</Badge>}
            {format && <Badge variant="muted" size="sm">{format}</Badge>}
            {year && <Badge variant="outline" size="sm">{year}</Badge>}
            {rating && <Badge variant="outline" size="sm">{rating}</Badge>}
          </div>
        )}

        {views && (
          <p className="text-[10px] sm:text-xs dark:text-untold-muted light:text-gray-400 mt-1">{views} views</p>
        )}
      </div>
    </article>
  );
}

export function VideoCardSkeleton({ variant = 'default', fluid = false }) {
  const isShort = variant === 'short';
  const widthClass = fluid
    ? 'w-full'
    : isShort
      ? 'w-[165px] sm:w-[180px]'
      : 'w-[220px] sm:w-[260px]';
  return (
    <div className={`shrink-0 ${widthClass}`}>
      <div className={`${fluid ? 'rounded-t-xl' : 'rounded-lg'} skeleton ${isShort ? 'aspect-[9/16]' : 'aspect-video'}`} />
      <div className={`${fluid ? 'p-3' : 'mt-2'} space-y-2`}>
        <div className="h-4 w-3/4 rounded skeleton" />
        <div className="h-3 w-1/2 rounded skeleton" />
      </div>
    </div>
  );
}
