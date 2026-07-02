import { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { SearchIcon, CloseIcon } from '../icons';
import { globalSearch } from '../../utils/exploreSearch';

function SearchSection({ label, items, renderItem }) {
  if (!items?.length) return null;
  return (
    <>
      <li className="px-4 py-1.5 text-[10px] font-semibold uppercase tracking-wider dark:text-untold-muted light:text-gray-400">
        {label}
      </li>
      {items.map(renderItem)}
    </>
  );
}

function SearchRow({ to, onClose, title, subtitle, image }) {
  return (
    <li>
      <Link
        to={to}
        onClick={onClose}
        className="flex gap-3 px-4 py-2.5 hover:dark:bg-white/5 hover:light:bg-black/5 transition-colors"
      >
        {image && <img src={image} alt="" className="w-14 h-10 rounded object-cover shrink-0" />}
        <div className="min-w-0">
          <p className="text-sm font-medium truncate dark:text-untold-white light:text-black">{title}</p>
          {subtitle && <p className="text-xs dark:text-untold-muted light:text-gray-500">{subtitle}</p>}
        </div>
      </Link>
    </li>
  );
}

export default function SearchBar({ className = '' }) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [data, setData] = useState(null);
  const inputRef = useRef(null);

  const close = () => setOpen(false);

  useEffect(() => {
    if (open) inputRef.current?.focus();
  }, [open]);

  useEffect(() => {
    if (!query.trim()) {
      setData(null);
      return;
    }
    let cancelled = false;
    globalSearch(query).then((result) => {
      if (!cancelled) setData(result);
    }).catch(() => {
      if (!cancelled) setData({ videos: [], events: [], news: [], people: [], verticals: [], topics: [], companies: [] });
    });
    return () => { cancelled = true; };
  }, [query]);

  useEffect(() => {
    const onKey = (e) => {
      if (e.key === 'Escape') setOpen(false);
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, []);

  const hasResults = data && (
    data.videos.length ||
    data.events.length ||
    data.news.length ||
    data.people.length ||
    data.verticals.length ||
    data.topics.length ||
    data.companies.length
  );

  return (
    <div className={`relative ${className}`}>
      <button type="button" onClick={() => setOpen((o) => !o)} aria-label="Search" className="site-header-icon-btn">
        <SearchIcon className="w-5 h-5" />
      </button>

      {open && (
        <>
          <div className="fixed inset-0 z-[70] bg-black/60 backdrop-blur-sm" onClick={close} />
          <div className="fixed left-1/2 top-20 z-[80] w-[min(100%,36rem)] -translate-x-1/2 px-4">
            <div className="rounded-xl dark:bg-untold-card light:bg-white shadow-2xl border dark:border-untold-border light:border-gray-200 overflow-hidden animate-scale-in">
              <div className="flex items-center gap-2 px-4 py-3 border-b dark:border-untold-border light:border-gray-100">
                <SearchIcon className="w-5 h-5 dark:text-untold-muted light:text-gray-400 shrink-0" />
                <input
                  ref={inputRef}
                  type="search"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Search documentaries, people, companies, topics…"
                  className="flex-1 bg-transparent text-sm outline-none dark:text-untold-white light:text-black placeholder:dark:text-untold-muted placeholder:light:text-gray-400"
                />
                <button type="button" onClick={close} aria-label="Close search">
                  <CloseIcon className="w-5 h-5 dark:text-untold-muted light:text-gray-500" />
                </button>
              </div>
              <ul className="max-h-[min(70vh,24rem)] overflow-y-auto py-2">
                {!query.trim() ? (
                  <li className="px-4 py-6 text-sm text-center dark:text-untold-muted light:text-gray-500">
                    Search originals, legends, business, Hollywood, sports & more
                  </li>
                ) : !hasResults ? (
                  <li className="px-4 py-6 text-sm text-center dark:text-untold-muted light:text-gray-500">
                    No results for &ldquo;{query}&rdquo;
                  </li>
                ) : (
                  <>
                    <SearchSection
                      label="Documentaries & Series"
                      items={data.videos}
                      renderItem={(v) => (
                        <SearchRow
                          key={v.id}
                          to={`/video/${v.id}`}
                          onClose={close}
                          title={v.title}
                          subtitle={`${v.vertical || v.sport || ''} · ${v.format || v.categoryName || ''}`}
                          image={v.thumbnail || v.image}
                        />
                      )}
                    />
                    <SearchSection
                      label="People & Legends"
                      items={data.people}
                      renderItem={(p) => (
                        <SearchRow key={p.id} to={`/video/${p.id}`} onClose={close} title={p.name} subtitle={p.sport} image={p.image} />
                      )}
                    />
                    <SearchSection
                      label="Companies & Business"
                      items={data.companies}
                      renderItem={(c) => (
                        <SearchRow key={c.id} to={`/video/${c.id}`} onClose={close} title={c.name} subtitle="Business" image={c.image} />
                      )}
                    />
                    <SearchSection
                      label="Collections"
                      items={data.verticals}
                      renderItem={(v) => (
                        <SearchRow key={v.id} to={`/explore${v.explore}`} onClose={close} title={v.name} subtitle="Browse collection" />
                      )}
                    />
                    <SearchSection
                      label="Topics & Tags"
                      items={data.topics}
                      renderItem={(t) => (
                        <SearchRow key={t.id} to={`/explore?q=${encodeURIComponent(t.name)}`} onClose={close} title={t.name} subtitle="Topic" />
                      )}
                    />
                    <SearchSection
                      label="Events"
                      items={data.events}
                      renderItem={(e) => (
                        <SearchRow key={e.id} to="/events" onClose={close} title={e.eventName} subtitle={`${e.sport} · ${e.status}`} image={e.thumbnail} />
                      )}
                    />
                    <SearchSection
                      label="News"
                      items={data.news}
                      renderItem={(n) => (
                        <SearchRow key={n.id} to="/news" onClose={close} title={n.title} subtitle={n.sport} image={n.thumbnail} />
                      )}
                    />
                  </>
                )}
              </ul>
              {query.trim() && (
                <Link
                  to={`/explore?q=${encodeURIComponent(query)}`}
                  onClick={close}
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
