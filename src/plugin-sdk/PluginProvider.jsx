import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { activatePlugins, runHooks } from './registry';
import './samples';

const PluginRuntimeContext = createContext({
  installations: [],
  isLoading: true,
  runHooks: async (_hook, payload) => payload,
});

/**
 * Loads enabled plugins from the API and activates frontend handlers.
 */
export function PluginProvider({ fetchRuntime, children }) {
  const { data: installations = [], isLoading } = useQuery({
    queryKey: ['plugin-runtime'],
    queryFn: fetchRuntime,
    staleTime: 60_000,
  });

  const [ready, setReady] = useState(false);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      await activatePlugins(installations);
      if (!cancelled) setReady(true);
    })();
    return () => {
      cancelled = true;
      setReady(false);
    };
  }, [installations]);

  const runHookChain = useCallback((hookName, payload) => runHooks(hookName, payload), []);

  const value = useMemo(
    () => ({
      installations,
      isLoading: isLoading || !ready,
      runHooks: runHookChain,
    }),
    [installations, isLoading, ready, runHookChain],
  );

  return <PluginRuntimeContext.Provider value={value}>{children}</PluginRuntimeContext.Provider>;
}

export function usePluginRuntime() {
  return useContext(PluginRuntimeContext);
}

/** Run a hook chain with loading guard. */
export function usePluginHooks(hookName) {
  const { runHooks: run } = usePluginRuntime();
  return useCallback((payload) => run(hookName, payload), [hookName, run]);
}

export default PluginProvider;
