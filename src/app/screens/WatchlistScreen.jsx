import { useNavigate } from 'react-router-dom';
import { useWatchlist } from '../context/WatchlistContext';
import MobileVideoCard from '../components/MobileVideoCard';
import { BookmarkIcon, PlayIcon } from '../../components/icons';

export default function WatchlistScreen() {
  const { items } = useWatchlist();
  const navigate = useNavigate();

  return (
    <div className="pb-4 animate-fade-in">
      <div className="px-4 pt-3 pb-2">
        <h1 className="text-xl font-display font-bold dark:text-untold-white light:text-black">My List</h1>
      </div>

      {items.length === 0 ? (
        <div className="flex flex-col items-center justify-center px-8 pt-24 text-center">
          <div className="w-16 h-16 rounded-full dark:bg-untold-surface light:bg-gray-100 flex items-center justify-center mb-5">
            <BookmarkIcon className="w-7 h-7 dark:text-untold-muted light:text-gray-400" />
          </div>
          <h2 className="text-lg font-semibold dark:text-untold-white light:text-black">
            Your list is empty
          </h2>
          <p className="text-sm dark:text-untold-muted light:text-gray-500 mt-2 leading-relaxed">
            Save documentaries and shows to watch later. Tap the + icon on any title.
          </p>
          <button
            onClick={() => navigate('/app/originals')}
            className="mt-6 px-6 py-2.5 rounded-xl bg-untold-gold text-untold-dark text-sm font-semibold
              active:scale-[0.98] transition-transform"
          >
            Browse Originals
          </button>
        </div>
      ) : (
        <div className="px-4 mt-2">
          <p className="text-xs dark:text-untold-muted light:text-gray-400 mb-4">
            {items.length} title{items.length !== 1 ? 's' : ''} saved
          </p>

          <div className="space-y-3">
            {items.map((item) => (
              <div
                key={item.id}
                className="flex items-center gap-3 p-2 rounded-xl
                  dark:bg-untold-surface/50 light:bg-gray-50 active:scale-[0.99] transition-transform"
                onClick={() => navigate(`/app/watch/${item.id}`)}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => e.key === 'Enter' && navigate(`/app/watch/${item.id}`)}
              >
                <div className="relative w-24 h-14 rounded-lg overflow-hidden shrink-0">
                  <img src={item.image} alt="" className="w-full h-full object-cover" />
                  <div className="absolute inset-0 flex items-center justify-center bg-black/30">
                    <PlayIcon className="w-4 h-4 text-white" />
                  </div>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium dark:text-untold-white light:text-black truncate">
                    {item.title}
                  </p>
                  <p className="text-xs dark:text-untold-muted light:text-gray-500 mt-0.5">
                    {item.category} · {item.duration}
                  </p>
                </div>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-2 gap-3 mt-8">
            {items.map((item) => (
              <div key={`grid-${item.id}`} className="[&>article]:w-full">
                <MobileVideoCard item={item} />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
