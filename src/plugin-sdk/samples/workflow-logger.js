import { createPlugin, EVENTS, HOOKS } from '../registry';

createPlugin({
  manifest: {
    slug: 'workflow-logger',
    name: 'Workflow Logger',
    hooks: [HOOKS.WORKFLOW_AFTER_NODE],
    subscribes: [EVENTS.WORKFLOW_NODE_COMPLETED],
  },
  setup(api) {
    const level = api.getSetting('log_level', 'info');
    const includePayload = api.getSetting('include_payload', false);

    api.onEvent(EVENTS.WORKFLOW_NODE_COMPLETED, (payload) => {
      const msg = `[workflow-logger] node ${payload.node_id} completed (run ${payload.run_id})`;
      if (level === 'debug' && includePayload) {
        console.debug(msg, payload.output);
      } else {
        console.info(msg);
      }
    });

    api.onHook(HOOKS.WORKFLOW_AFTER_NODE, (payload) => {
      if (level === 'debug') {
        console.debug('[workflow-logger] after node', payload.node_id);
      }
      return {};
    });
  },
});
