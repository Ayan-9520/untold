import { createContext, useContext, useState, useEffect, useCallback, useMemo } from 'react';
import { contentApi } from '../api/content';
import streamingApi from '../api/streaming';
import { useWebAuth } from './WebAuthContext';

const VOTES_KEY = 'untold-votes';
const HISTORY_KEY = 'untold-watch-history';
const MAX_HISTORY = 12;

const EngagementContext = createContext(null);

function loadJson(key, fallback) {
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : fallback;
  } catch {
    return fallback;
  }
}

export function EngagementProvider({ children }) {
  const { isAuthenticated } = useWebAuth();
  const [votes, setVotes] = useState({});
  const [watchHistory, setWatchHistory] = useState([]);
  const [serverContinue, setServerContinue] = useState([]);
  const [catalogPool, setCatalogPool] = useState([]);

  useEffect(() => {
    setVotes(loadJson(VOTES_KEY, {}));
    setWatchHistory(loadJson(HISTORY_KEY, []));
  }, []);

  useEffect(() => {
    if (!isAuthenticated) {
      setServerContinue([]);
      return;
    }
    streamingApi.getContinueWatching(12).then((items) => {
      setServerContinue(
        items.map((item) => ({
          id: item.video_id,
          title: item.title,
          image: item.image_url,
          progress: (item.progress_percent || 0) / 100,
          watchedAt: Date.now(),
        }))
      );
    }).catch(() => setServerContinue([]));
  }, [isAuthenticated]);

  useEffect(() => {
    contentApi.getTrending()
      .then(({ data }) => setCatalogPool(data))
      .catch(() => setCatalogPool([]));
  }, []);

  const persistVotes = useCallback((next) => {
    localStorage.setItem(VOTES_KEY, JSON.stringify(next));
    return next;
  }, []);

  const persistHistory = useCallback((next) => {
    localStorage.setItem(HISTORY_KEY, JSON.stringify(next));
    return next;
  }, []);

  const vote = useCallback((pollId, optionId, type = 'debate') => {
    const key = `${type}:${pollId}`;
    setVotes((prev) => {
      if (prev[key]) return prev;
      const next = { ...prev, [key]: optionId };
      persistVotes(next);
      return next;
    });
  }, [persistVotes]);

  const getUserVote = useCallback(
    (pollId, type = 'debate') => votes[`${type}:${pollId}`] || null,
    [votes]
  );

  const getVoteCounts = useCallback((item, type = 'debate') => {
    if (!item?.options) return [];
    const stored = loadJson('untold-vote-counts', {});
    const prefix = `${type}:${item.id}:`;
    return item.options.map((opt) => {
      const boost = stored[`${prefix}${opt.id}`] || 0;
      const userVoted = getUserVote(item.id, type) === opt.id;
      return {
        ...opt,
        votes: opt.votes + boost + (userVoted ? 1 : 0),
      };
    });
  }, [getUserVote]);

  const recordWatch = useCallback((video, progress = 0.15) => {
    if (!video?.id) return;
    setWatchHistory((prev) => {
      const entry = {
        id: video.id,
        title: video.title,
        image: video.image || video.thumbnail,
        sport: video.sport,
        category: video.category,
        progress: Math.min(1, Math.max(progress, 0.05)),
        watchedAt: Date.now(),
      };
      const filtered = prev.filter((h) => h.id !== video.id);
      const next = persistHistory([entry, ...filtered].slice(0, MAX_HISTORY));
      return next;
    });
  }, [persistHistory]);

  const updateProgress = useCallback((videoId, progress) => {
    setWatchHistory((prev) => {
      const next = prev.map((h) =>
        h.id === videoId ? { ...h, progress: Math.min(1, progress), watchedAt: Date.now() } : h
      );
      persistHistory(next);
      return next;
    });
  }, [persistHistory]);

  const clearHistory = useCallback(() => {
    setWatchHistory(persistHistory([]));
  }, [persistHistory]);

  const recommendations = useMemo(() => {
    if (watchHistory.length === 0) {
      return catalogPool.slice(0, 8);
    }

    const watchedIds = new Set(watchHistory.map((h) => h.id));
    const sports = [...new Set(watchHistory.map((h) => h.sport).filter(Boolean))];
    const categories = [...new Set(watchHistory.map((h) => h.category).filter(Boolean))];

    const scored = catalogPool
      .filter((v) => !watchedIds.has(v.id))
      .map((v) => {
        let score = 0;
        if (sports.includes(v.sport) || sports.includes(v.category)) score += 3;
        if (categories.includes(v.category)) score += 2;
        if (v.trending) score += 1;
        if (v.featured) score += 1;
        return { ...v, score };
      })
      .sort((a, b) => b.score - a.score);

    return scored.slice(0, 8);
  }, [watchHistory, catalogPool]);

  const continueWatching = useMemo(() => {
    const merged = serverContinue.length ? serverContinue : watchHistory;
    return merged.filter((h) => h.progress < 0.95).slice(0, 6);
  }, [watchHistory, serverContinue]);

  return (
    <EngagementContext.Provider
      value={{
        vote,
        getUserVote,
        getVoteCounts,
        watchHistory,
        recordWatch,
        updateProgress,
        clearHistory,
        recommendations,
        continueWatching,
      }}
    >
      {children}
    </EngagementContext.Provider>
  );
}

export function useEngagement() {
  const ctx = useContext(EngagementContext);
  if (!ctx) throw new Error('useEngagement must be used within EngagementProvider');
  return ctx;
}
