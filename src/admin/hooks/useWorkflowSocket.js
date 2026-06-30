import { useEffect, useRef } from 'react';

const WS_BASE = import.meta.env.VITE_WS_URL || `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}`;

export function useWorkflowSocket({ token, runId, onEvent }) {
  const wsRef = useRef(null);
  const onEventRef = useRef(onEvent);
  onEventRef.current = onEvent;

  useEffect(() => {
    if (!token || !runId) return undefined;

    const ws = new WebSocket(`${WS_BASE}/ws/studio?token=${encodeURIComponent(token)}`);
    wsRef.current = ws;

    ws.onmessage = (ev) => {
      try {
        const data = JSON.parse(ev.data);
        if (data.type === 'workflow_event' && data.run_id === runId) {
          onEventRef.current?.(data);
        }
      } catch {
        /* ignore */
      }
    };

    return () => {
      ws.close();
      wsRef.current = null;
    };
  }, [token, runId]);
}
