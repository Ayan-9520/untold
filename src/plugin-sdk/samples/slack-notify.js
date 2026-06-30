import { createPlugin, EVENTS } from '../registry';

createPlugin({
  manifest: {
    slug: 'slack-notify',
    name: 'Slack Notify',
    subscribes: ['workflow.run.finished', 'publish.completed', 'collab.comment.created'],
  },
  setup(api) {
    if (!api.hasPermission('webhook.send')) return;

    const format = (event, payload) => {
      if (event === EVENTS.WORKFLOW_RUN_FINISHED) {
        return `Workflow #${payload.run_id} finished (${payload.status})`;
      }
      if (event === EVENTS.PUBLISH_COMPLETED) {
        return `Published to ${payload.platform}`;
      }
      if (event === EVENTS.COLLAB_COMMENT_CREATED) {
        return `New comment on project ${payload.project_id}`;
      }
      return `Studio event: ${event}`;
    };

    api.onEvent(EVENTS.WORKFLOW_RUN_FINISHED, (payload) => {
      if (!api.getSetting('notify_on_workflow', true)) return;
      console.info('[slack-notify]', format(EVENTS.WORKFLOW_RUN_FINISHED, payload));
    });
    api.onEvent(EVENTS.PUBLISH_COMPLETED, (payload) => {
      if (!api.getSetting('notify_on_publish', true)) return;
      console.info('[slack-notify]', format(EVENTS.PUBLISH_COMPLETED, payload));
    });
    api.onEvent(EVENTS.COLLAB_COMMENT_CREATED, (payload) => {
      if (!api.getSetting('notify_on_comments', false)) return;
      console.info('[slack-notify]', format(EVENTS.COLLAB_COMMENT_CREATED, payload));
    });
  },
});
