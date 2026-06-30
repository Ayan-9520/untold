import { createPlugin, HOOKS } from '../registry';

createPlugin({
  manifest: {
    slug: 'dashboard-widgets',
    name: 'Studio Widgets Pack',
    hooks: [HOOKS.DASHBOARD_WIDGETS],
  },
  setup(api) {
    api.onHook(HOOKS.DASHBOARD_WIDGETS, () => {
      const widgets = [];
      if (api.getSetting('show_pipeline_health', true)) {
        widgets.push({ id: 'pipeline-health', title: 'Pipeline Health', type: 'stat', value: '98%' });
      }
      if (api.getSetting('show_ai_spend', true) && api.hasPermission('admin.read')) {
        widgets.push({ id: 'ai-spend', title: 'AI Spend (7d)', type: 'currency', value: '$124' });
      }
      if (api.getSetting('show_team_activity', true)) {
        widgets.push({ id: 'team-activity', title: 'Team Activity', type: 'list', items: ['3 comments', '1 approval'] });
      }
      return { widgets };
    });
  },
});
