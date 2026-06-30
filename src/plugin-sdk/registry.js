/**
 * UNTOLD Plugin SDK — core registry (hooks, events, plugin registration).
 */

const plugins = new Map();
const hookHandlers = new Map();
const eventListeners = new Map();

export function createPlugin(definition) {
  const slug = definition.manifest?.slug;
  if (!slug) throw new Error('Plugin manifest.slug is required');
  plugins.set(slug, definition);
  return definition;
}

export function getPlugin(slug) {
  return plugins.get(slug);
}

export function getAllPlugins() {
  return Array.from(plugins.values());
}

export async function activatePlugins(installations = []) {
  hookHandlers.clear();
  eventListeners.clear();

  for (const inst of installations) {
    const def = plugins.get(inst.slug);
    if (!def?.setup) continue;
    await def.setup(buildPluginAPI(inst));
  }
}

function buildPluginAPI(inst) {
  const slug = inst.slug;
  const settings = inst.settings || {};
  const grantedPermissions = inst.granted_permissions || [];

  return {
    slug,
    settings,
    grantedPermissions,
    onHook(hookName, handler) {
      if (!hookHandlers.has(hookName)) hookHandlers.set(hookName, []);
      hookHandlers.get(hookName).push({ slug, handler });
    },
    onEvent(eventName, handler) {
      if (!eventListeners.has(eventName)) eventListeners.set(eventName, []);
      eventListeners.get(eventName).push({ slug, handler });
    },
    emit(eventName, payload = {}) {
      dispatchEvent(eventName, payload);
    },
    hasPermission(permission) {
      return grantedPermissions.includes(permission);
    },
    getSetting(key, defaultValue) {
      return settings[key] ?? defaultValue;
    },
  };
}

export async function runHooks(hookName, payload = {}) {
  const handlers = hookHandlers.get(hookName) || [];
  let merged = { ...payload };
  for (const { handler } of handlers) {
    try {
      const result = await handler(merged);
      if (result && typeof result === 'object') merged = { ...merged, ...result };
    } catch (err) {
      console.error(`[plugin-sdk] Hook ${hookName} failed`, err);
    }
  }
  return merged;
}

export function dispatchEvent(eventName, payload = {}) {
  const listeners = eventListeners.get(eventName) || [];
  for (const { slug, handler } of listeners) {
    try {
      handler(payload);
    } catch (err) {
      console.error(`[plugin-sdk] Event ${eventName} handler failed (${slug})`, err);
    }
  }
}

export const HOOKS = {
  WORKFLOW_BEFORE_NODE: 'workflow.before_node',
  WORKFLOW_AFTER_NODE: 'workflow.after_node',
  SEO_FORMAT_TITLE: 'seo.format_title',
  SEO_FORMAT_DESCRIPTION: 'seo.format_description',
  SCRIPT_BEFORE_EXPORT: 'script.before_export',
  DASHBOARD_WIDGETS: 'dashboard.widgets',
  NAV_ITEMS: 'nav.items',
};

export const EVENTS = {
  WORKFLOW_RUN_STARTED: 'workflow.run.started',
  WORKFLOW_RUN_FINISHED: 'workflow.run.finished',
  WORKFLOW_NODE_COMPLETED: 'workflow.node.completed',
  PUBLISH_COMPLETED: 'publish.completed',
  COLLAB_COMMENT_CREATED: 'collab.comment.created',
  PLUGIN_INSTALLED: 'plugin.installed',
};

export const PERMISSIONS = {
  WEBHOOK_SEND: 'webhook.send',
  NOTIFICATION_SEND: 'notification.send',
  WORKFLOW_READ: 'workflow.read',
  PROJECT_READ: 'project.read',
  COLLAB_READ: 'collab.read',
};
