import { useEffect, useRef } from 'react';

const WS_BASE = import.meta.env.VITE_WS_URL || `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}`;

export function useCollaborationSocket({ token, projectId, resourceType, resourceId, onEvent }) {
  const wsRef = useRef(null);
  const onEventRef = useRef(onEvent);
  onEventRef.current = onEvent;

  useEffect(() => {
    if (!token || !projectId) return undefined;

    const ws = new WebSocket(`${WS_BASE}/ws/studio?token=${encodeURIComponent(token)}`);
    wsRef.current = ws;

    ws.onopen = () => {
      ws.send(
        JSON.stringify({
          type: 'join_room',
          project_id: projectId,
          resource_type: resourceType || 'project',
          resource_id: resourceId,
        }),
      );
    };

    ws.onmessage = (ev) => {
      try {
        const data = JSON.parse(ev.data);
        if (data.type === 'collaboration_event' || data.type === 'connected') {
          onEventRef.current?.(data);
        }
      } catch {
        /* ignore */
      }
    };

    const ping = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) ws.send(JSON.stringify({ type: 'ping' }));
    }, 25000);

    return () => {
      clearInterval(ping);
      ws.close();
      wsRef.current = null;
    };
  }, [token, projectId, resourceType, resourceId]);

  const sendPatch = (payload) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({
          type: 'collab_patch',
          project_id: projectId,
          resource_type: resourceType,
          resource_id: resourceId,
          ...payload,
        }),
      );
    }
  };

  return { sendPatch };
}
