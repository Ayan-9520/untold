/**
 * UNTOLD Agent SDK — frontend helpers for agent runtime integration.
 */

const AGENT_EVENTS = {
  RUN_STARTED: 'agent.run.started',
  RUN_COMPLETED: 'agent.run.completed',
  MESSAGE_RECEIVED: 'agent.message.received',
};

const AGENT_PERMISSIONS = [
  'ai.generate',
  'project.read',
  'project.write',
  'publish.dispatch',
  'memory.read',
  'memory.write',
  'communicate.send',
  'communicate.receive',
  'schedule.manage',
  'analytics.read',
];

/**
 * Create an agent extension manifest for registration.
 */
export function createAgentManifest({ slug, name, description, permissions = [], hooks = {} }) {
  return {
    slug,
    name,
    description,
    permissions,
    hooks,
    version: '1.0.0',
  };
}

/**
 * Dispatch a custom agent event to registered listeners.
 */
export function dispatchAgentEvent(eventName, payload, listeners = []) {
  return listeners
    .filter((l) => l.event === eventName || l.event === '*')
    .map((l) => {
      try {
        return l.handler(payload);
      } catch (err) {
        console.error(`Agent SDK listener error (${eventName}):`, err);
        return null;
      }
    });
}

/**
 * Build API paths for agent platform endpoints (relative to admin API base).
 */
export function agentPlatformPaths(installationId) {
  const base = `/studio/platform/agent-platform/installations/${installationId}`;
  return {
    memory: `${base}/memory`,
    schedules: `${base}/schedules`,
    messages: `${base}/messages`,
    analytics: `${base}/analytics`,
    run: `${base}/run`,
  };
}

export { AGENT_EVENTS, AGENT_PERMISSIONS };
