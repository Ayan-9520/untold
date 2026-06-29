import { Link } from 'react-router-dom';
import { PlayIcon } from '../icons';

export default function ShortsCard({ title, image, duration, views, to = '/shorts' }) {
  return (
    <Link
      to={to}
      className="group relative shrink-0 w-[140px] sm:w-[160px] card-hover"
    >
      <div className="relative aspect-[9/14] overflow-hidden rounded-xl dark:bg-untold-surface light:bg-gray-100">
        <img
          src={image}
          alt={title}
          loading="lazy"
          className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent" />
        <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
          <div className="w-10 h-10 rounded-full bg-untold-gold/90 text-untold-dark flex items-center justify-center shadow-lg">
            <PlayIcon className="w-4 h-4 ml-0.5" />
          </div>
        </div>
        {duration && (
          <span className="absolute bottom-2 right-2 text-[10px] font-medium px-1.5 py-0.5 rounded bg-black/70 text-white">
            {duration}
          </span>
        )}
      </div>
      <h3 className="mt-2 text-sm font-semibold line-clamp-2 dark:text-untold-white light:text-black group-hover:text-untold-gold transition-colors">
        {title}
      </h3>
      {views && (
        <p className="text-xs dark:text-untold-muted light:text-gray-400 mt-0.5">{views} views</p>
      )}
    </Link>
  );
}
