import { createPlugin, HOOKS } from '../registry';

createPlugin({
  manifest: {
    slug: 'custom-seo-formatter',
    name: 'Custom SEO Formatter',
    hooks: [HOOKS.SEO_FORMAT_TITLE, HOOKS.SEO_FORMAT_DESCRIPTION],
  },
  setup(api) {
    api.onHook(HOOKS.SEO_FORMAT_TITLE, (payload) => {
      const title = payload.title || '';
      const prefix = api.getSetting('title_prefix', '');
      const suffix = api.getSetting('title_suffix', ' | UNTOLD');
      const maxLen = Number(api.getSetting('max_title_length', 60));
      let formatted = `${prefix}${title}${suffix}`.trim();
      if (formatted.length > maxLen) formatted = `${formatted.slice(0, maxLen - 3)}...`;
      return { title: formatted };
    });

    api.onHook(HOOKS.SEO_FORMAT_DESCRIPTION, (payload) => {
      let description = payload.description || '';
      const append = api.getSetting('description_append', '');
      if (append && !description.includes(append)) {
        description = `${description} ${append}`.trim();
      }
      return { description };
    });
  },
});
