/** Deep-merge locale patches onto the English base (arrays replaced, not merged). */
export function mergeLocale(base, patch) {
  if (!patch) return { ...base };
  const result = { ...base };
  for (const [key, value] of Object.entries(patch)) {
    if (value && typeof value === 'object' && !Array.isArray(value)) {
      result[key] = mergeLocale(base[key] || {}, value);
    } else {
      result[key] = value;
    }
  }
  return result;
}
