import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { appApi } from '../../api/appApi';
import { useAppUI } from '../context/AppUIContext';
import { CloseIcon, SearchIcon, PlayIcon } from '../../components/icons';

export default function SearchOverlay() {
  const { searchOpen, closeSearch } = useAppUI();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const inputRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (searchOpen) {
      setTimeout(() => inputRef.current?.focus(), 100);
    } else {
      setQuery('');
      setResults([]);
    }
  }, [searchOpen]);

  useEffect(() => {
    if (!query.trim()) {
      setResults([]);
      return;
    }
    const timer = setTimeout(async () => {
      setLoading(true);
      try {
        const { data } = await appApi.search(query);
        setResults(data);
      } finally {
        setLoading(false);
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [query]);

  if (!searchOpen) return null;

  const handleSelect = (item) => {
    closeSearch();
    if (item.duration && item.duration.includes(':')) {
      navigate('/app/shorts');
    } else {
      navigate(`/app/watch/${item.id}`);
    }
  };

  return (
    <div className="fixed inset-0 z-50 mx-auto max-w-[430px] animate-fade-in">
      <div className="absolute inset-0 dark:bg-untold-dark/95 light:bg-white/95 backdrop-blur-xl" />

      <div className="relative flex flex-col h-full pt-[env(safe-area-inset-top)]">
        <div className="flex items-center gap-3 px-4 py-3">
          <div className="flex-1 flex items-center gap-2 rounded-xl px-3 py-2.5
            dark:bg-untold-surface light:bg-gray-100">
            <SearchIcon className="w-4 h-4 dark:text-untold-muted light:text-gray-400 shrink-0" />
            <input
              ref={inputRef}
              type="search"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search documentaries, shorts..."
              className="flex-1 bg-transparent text-sm outline-none dark:text-untold-white light:text-black placeholder:dark:text-untold-muted placeholder:light:text-gray-400"
            />
          </div>
          <button
            onClick={closeSearch}
            className="p-2 rounded-full dark:hover:bg-white/10 light:hover:bg-black/5"
            aria-label="Close search"
          >
            <CloseIcon className="w-5 h-5" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-4 pb-8">
          {loading && (
            <div className="space-y-3 mt-2">
              {[1, 2, 3].map((i) => (
                <div key={i} className="flex gap-3">
                  <div className="w-20 h-12 rounded-lg skeleton" />
                  <div className="flex-1 space-y-2 py-1">
                    <div className="h-3 w-3/4 rounded skeleton" />
                    <div className="h-2 w-1/2 rounded skeleton" />
                  </div>
                </div>
              ))}
            </div>
          )}

          {!loading && query && results.length === 0 && (
            <p className="text-center text-sm dark:text-untold-muted light:text-gray-500 mt-12">
              No results for &ldquo;{query}&rdquo;
            </p>
          )}

          {!query && (
            <div className="mt-4">
              <p className="text-xs font-medium uppercase tracking-wider dark:text-untold-muted light:text-gray-400 mb-3">
                Popular Searches
              </p>
              {['Malice at the Palace', 'Jordan', 'Rivalries', 'Boxing'].map((term) => (
                <button
                  key={term}
                  onClick={() => setQuery(term)}
                  className="block w-full text-left px-3 py-2.5 rounded-lg text-sm
                    dark:text-untold-white light:text-black
                    dark:hover:bg-white/5 light:hover:bg-black/5 transition-colors"
                >
                  {term}
                </button>
              ))}
            </div>
          )}

          {results.map((item) => (
            <button
              key={item.id}
              onClick={() => handleSelect(item)}
              className="flex w-full items-center gap-3 py-3 border-b dark:border-untold-border/50 light:border-gray-100
                hover:dark:bg-white/5 hover:light:bg-black/5 transition-colors text-left"
            >
              <div className="relative w-20 h-12 rounded-lg overflow-hidden shrink-0">
                <img src={item.image} alt="" className="w-full h-full object-cover" />
                <div className="absolute inset-0 flex items-center justify-center bg-black/30">
                  <PlayIcon className="w-4 h-4 text-white" />
                </div>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium dark:text-untold-white light:text-black truncate">
                  {item.title}
                </p>
                <p className="text-xs dark:text-untold-muted light:text-gray-500">
                  {item.category || item.duration}
                </p>
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
