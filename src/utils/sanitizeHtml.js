/**
 * Client-side HTML sanitization for AI-generated content.
 * Strips scripts, event handlers, and dangerous URLs before innerHTML use.
 */

const BLOCKED_TAGS = new Set([
  'SCRIPT',
  'STYLE',
  'IFRAME',
  'OBJECT',
  'EMBED',
  'LINK',
  'META',
  'BASE',
  'FORM',
]);

const ALLOWED_TAGS = new Set([
  'P',
  'BR',
  'B',
  'STRONG',
  'I',
  'EM',
  'U',
  'UL',
  'OL',
  'LI',
  'H1',
  'H2',
  'H3',
  'H4',
  'H5',
  'H6',
  'SPAN',
  'DIV',
  'BLOCKQUOTE',
  'PRE',
  'CODE',
]);

function isSafeUrl(url) {
  if (!url) return true;
  const trimmed = url.trim().toLowerCase();
  return !trimmed.startsWith('javascript:') && !trimmed.startsWith('data:text/html');
}

function sanitizeNode(node) {
  if (node.nodeType === Node.TEXT_NODE) return;

  if (node.nodeType !== Node.ELEMENT_NODE) {
    node.remove();
    return;
  }

  const el = /** @type {Element} */ (node);
  const tag = el.tagName.toUpperCase();

  if (BLOCKED_TAGS.has(tag) || !ALLOWED_TAGS.has(tag)) {
    const text = document.createTextNode(el.textContent || '');
    el.replaceWith(text);
    return;
  }

  for (const attr of [...el.attributes]) {
    const name = attr.name.toLowerCase();
    if (name.startsWith('on') || name === 'style' || name === 'srcdoc') {
      el.removeAttribute(attr.name);
      continue;
    }
    if ((name === 'href' || name === 'src') && !isSafeUrl(attr.value)) {
      el.removeAttribute(attr.name);
    }
  }

  for (const child of [...el.childNodes]) {
    sanitizeNode(child);
  }
}

/**
 * @param {string | null | undefined} dirty
 * @returns {string}
 */
export function sanitizeHtml(dirty) {
  if (!dirty) return '';
  if (typeof document === 'undefined') {
    return String(dirty).replace(/<[^>]*>/g, '');
  }
  const template = document.createElement('template');
  template.innerHTML = dirty;
  for (const child of [...template.content.childNodes]) {
    sanitizeNode(child);
  }
  return template.innerHTML;
}
