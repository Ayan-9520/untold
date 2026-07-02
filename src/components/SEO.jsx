import { useEffect } from 'react';

export default function SEO({ title, description, path = '', jsonLd = null }) {
  const fullTitle = title
    ? `${title} | UNTOLD`
    : 'UNTOLD — The Story Behind The Glory';
  const desc =
    description ||
    'Premium sports documentaries revealing the untold stories behind athletic greatness. Legends, rivalries, and moments that changed history.';

  useEffect(() => {
    document.title = fullTitle;

    const setMeta = (name, content, isProperty = false) => {
      const attr = isProperty ? 'property' : 'name';
      let el = document.querySelector(`meta[${attr}="${name}"]`);
      if (!el) {
        el = document.createElement('meta');
        el.setAttribute(attr, name);
        document.head.appendChild(el);
      }
      el.content = content;
    };

    setMeta('description', desc);
    setMeta('og:title', fullTitle, true);
    setMeta('og:description', desc, true);
    setMeta('og:url', `${window.location.origin}${path}`, true);
    setMeta('twitter:title', fullTitle);
    setMeta('twitter:description', desc);

    const canonical = document.querySelector('link[rel="canonical"]');
    if (canonical) {
      canonical.href = `${window.location.origin}${path}`;
    }

    const scriptId = 'untold-json-ld';
    let script = document.getElementById(scriptId);
    if (jsonLd) {
      if (!script) {
        script = document.createElement('script');
        script.id = scriptId;
        script.type = 'application/ld+json';
        document.head.appendChild(script);
      }
      script.textContent = JSON.stringify(jsonLd);
    } else if (script) {
      script.remove();
    }
  }, [fullTitle, desc, path, jsonLd]);

  return null;
}
