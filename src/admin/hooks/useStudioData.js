import { useState, useEffect, useCallback } from 'react';
import { studio } from '../api/adminApi';
import { ACTIVE_PRODUCTIONS } from '../../data/studioData';

/** Map API production to UI shape (compatible with legacy mock). */
export function mapProduction(p) {
  return {
    id: p.id,
    title: p.title,
    stage: p.stage,
    status: p.status,
    assignee: p.assignee,
    sources: p.sources_count,
    version: p.version,
    slug: p.slug,
  };
}

export function useStudioProductions(stage = null) {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [live, setLive] = useState(true);
  const [error, setError] = useState(null);

  const refresh = useCallback(() => {
    setLoading(true);
    setError(null);
    studio
      .listProductions(stage ? { stage } : {})
      .then((data) => {
        setItems((data.items || []).map(mapProduction));
        setLive(true);
      })
      .catch((err) => {
        const fallback = stage
          ? ACTIVE_PRODUCTIONS.filter((p) => p.stage === stage)
          : ACTIVE_PRODUCTIONS;
        setItems(fallback);
        setLive(false);
        setError(err.message);
      })
      .finally(() => setLoading(false));
  }, [stage]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { items, loading, live, error, refresh };
}

export function useStudioAgents() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [live, setLive] = useState(true);

  useEffect(() => {
    studio
      .getAgents()
      .then((d) => {
        setData(d);
        setLive(true);
      })
      .catch(() => {
        setLive(false);
        setData(null);
      })
      .finally(() => setLoading(false));
  }, []);

  return { data, loading, live };
}

export function useStudioAssets() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [live, setLive] = useState(true);

  useEffect(() => {
    studio
      .getAssets()
      .then((d) => {
        setData(d);
        setLive(true);
      })
      .catch(() => setLive(false))
      .finally(() => setLoading(false));
  }, []);

  return { data, loading, live };
}

export function useScriptsSummary() {
  const [summary, setSummary] = useState({ in_script: 0, approved: 0 });
  const [live, setLive] = useState(true);

  useEffect(() => {
    studio
      .getScriptsSummary()
      .then((d) => {
        setSummary(d);
        setLive(true);
      })
      .catch(() => {
        setLive(false);
        setSummary({ in_script: 2, approved: 2 });
      });
  }, []);

  return { summary, live };
}
