import { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { SearchIcon, CloseIcon } from '../icons';
import { searchVideos } from '../../data/videoCatalog';
import { searchEvents } from '../../data/eventsCatalog';
import { searchNews } from '../../data/newsCatalog';

export default function SearchBar({ className = '', overHero = false }) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [eventResults, setEventResults] = useState([]);
  const [newsResults, setNewsResults] = useState([]);
  const inputRef = useRef(null);

  useEffect(() => {
    if (open) inputRef.current?.focus();
  }, [open]);

  useEffect(() => {
    setResults(searchVideos(query).slice(0, 5));
    setEventResults(searchEvents(query).slice(0, 3));
    setNewsResults(searchNews(query).slice(0, 3));
  }, [query]);

  useEffect(() => {
    const onKey = (e) => {
      if (e.key === 'Escape') setOpen(false);
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, []);

  return (
    <div className={`relative ${className}`}>
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        aria-label="Search"
        className="site-header-icon-btn"
      >
        <SearchIcon className="w-5 h-5" />
      </button>

      {open && (
        <>
          <div className="fixed inset-0 z-[70] bg-black/40 backdrop-blur-sm" onClick={() => setOpen(false)} />
          <div className="fixed left-1/2 top-20 z-[80] w-[min(100%,32rem)] -translate-x-1/2 px-4">
            <div className="rounded-xl dark:bg-untold-surface light:bg-white shadow-2xl border dark:border-untold-border light:border-gray-200 overflow-hidden animate-scale-in">
              <div className="flex items-center gap-2 px-4 py-3 border-b dark:border-untold-border light:border-gray-100">
                <SearchIcon className="w-5 h-5 dark:text-untold-muted light:text-gray-400 shrink-0" />
                <input
                  ref={inputRef}
                  type="search"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Search documentaries, events, sports…"
                  className="flex-1 bg-transparent text-sm outline-none dark:text-untold-white light:text-black placeholder:dark:text-untold-muted placeholder:light:text-gray-400"
                />
                <button type="button" onClick={() => setOpen(false)} aria-label="Close search">
                  <CloseIcon className="w-5 h-5 dark:text-untold-muted light:text-gray-500" />
                </button>
              </div>
              <ul className="max-h-72 overflow-y-auto py-2">
                {results.length === 0 && eventResults.length === 0 && newsResults.length === 0 ? (
                  <li className="px-4 py-6 text-sm text-center dark:text-untold-muted light:text-gray-500">
                    {query ? 'No results found' : 'Start typing to search'}
                  </li>
                ) : (
                  <>
                    {eventResults.length > 0 && (
                      <>
                        <li className="px-4 py-1.5 text-[10px] font-semibold uppercase tracking-wider dark:text-untold-muted light:text-gray-400">
                          Events
                        </li>
                        {eventResults.map((e) => (
                          <li key={e.id}>
                            <Link
                              to="/events"
                              onClick={() => setOpen(false)}
                              className="flex gap-3 px-4 py-2.5 hover:dark:bg-white/5 hover:light:bg-black/5 transition-colors"
                            >
                              <img src={e.thumbnail} alt="" className="w-14 h-10 rounded object-cover shrink-0" />
                              <div className="min-w-0">
                                <p className="text-sm font-medium truncate dark:text-untold-white light:text-black">{e.eventName}</p>
                                <p className="text-xs dark:text-untold-muted light:text-gray-500">
                                  {e.sport} · {e.status}
                                </p>
                              </div>
                            </Link>
                          </li>
                        ))}
                      </>
                    )}
                    {newsResults.length > 0 && (
                      <>
                        <li className="px-4 py-1.5 text-[10px] font-semibold uppercase tracking-wider dark:text-untold-muted light:text-gray-400">
                          News
                        </li>
                        {newsResults.map((n) => (
                          <li key={n.id}>
                            <Link
                              to="/news"
                              onClick={() => setOpen(false)}
                              className="flex gap-3 px-4 py-2.5 hover:dark:bg-white/5 hover:light:bg-black/5 transition-colors"
                            >
                              <img src={n.thumbnail} alt="" className="w-14 h-10 rounded object-cover shrink-0" />
                              <div className="min-w-0">
                                <p className="text-sm font-medium truncate dark:text-untold-white light:text-black">{n.title}</p>
                                <p className="text-xs dark:text-untold-muted light:text-gray-500">{n.sport}</p>
                              </div>
                            </Link>
                          </li>
                        ))}
                      </>
                    )}
                    {results.length > 0 && (
                      <>
                        <li className="px-4 py-1.5 text-[10px] font-semibold uppercase tracking-wider dark:text-untold-muted light:text-gray-400">
                          Videos
                        </li>
                        {results.map((v) => (
                          <li key={v.id}>
                            <Link
                              to={`/video/${v.id}`}
                              onClick={() => setOpen(false)}
                              className="flex gap-3 px-4 py-2.5 hover:dark:bg-white/5 hover:light:bg-black/5 transition-colors"
                            >
                              <img src={v.thumbnail || v.image} alt="" className="w-14 h-10 rounded object-cover shrink-0" />
                              <div className="min-w-0">
                                <p className="text-sm font-medium truncate dark:text-untold-white light:text-black">{v.title}</p>
                                <p className="text-xs dark:text-untold-muted light:text-gray-500">{v.sport} · {v.categoryName}</p>
                              </div>
                            </Link>
                          </li>
                        ))}
                      </>
                    )}
                  </>
                )}
              </ul>
              {query && (
                <Link
                  to={`/explore?q=${encodeURIComponent(query)}`}
                  onClick={() => setOpen(false)}
                  className="block px-4 py-3 text-sm text-center font-medium text-untold-gold border-t dark:border-untold-border light:border-gray-100 hover:dark:bg-white/5"
                >
                  View all results
                </Link>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
