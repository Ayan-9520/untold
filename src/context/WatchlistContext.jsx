import { createContext, useContext, useState, useEffect, useCallback } from 'react';

const WATCHLIST_KEY = 'untold-watchlist';

const WatchlistContext = createContext(null);

export function WatchlistProvider({ children }) {
  const [items, setItems] = useState([]);

  useEffect(() => {
    try {
      const stored = localStorage.getItem(WATCHLIST_KEY);
      if (stored) setItems(JSON.parse(stored));
    } catch {
      setItems([]);
    }
  }, []);

  const persist = useCallback((next) => {
    localStorage.setItem(WATCHLIST_KEY, JSON.stringify(next));
    return next;
  }, []);

  const addToWatchlist = useCallback((item) => {
    setItems((prev) => {
      if (prev.some((i) => i.id === item.id)) return prev;
      return persist([...prev, { ...item, addedAt: Date.now() }]);
    });
  }, [persist]);

  const removeFromWatchlist = useCallback((id) => {
    setItems((prev) => persist(prev.filter((i) => i.id !== id)));
  }, [persist]);

  const isInWatchlist = useCallback((id) => items.some((i) => i.id === id), [items]);

  const toggleWatchlist = useCallback(
    (item) => {
      if (isInWatchlist(item.id)) removeFromWatchlist(item.id);
      else addToWatchlist(item);
    },
    [isInWatchlist, addToWatchlist, removeFromWatchlist]
  );

  return (
    <WatchlistContext.Provider
      value={{ items, addToWatchlist, removeFromWatchlist, isInWatchlist, toggleWatchlist }}
    >
      {children}
    </WatchlistContext.Provider>
  );
}

export function useWatchlist() {
  const ctx = useContext(WatchlistContext);
  if (!ctx) throw new Error('useWatchlist must be used within WatchlistProvider');
  return ctx;
}
