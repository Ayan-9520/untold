export default function SeoMetadataForm({ values, onChange }) {
  return (
    <div className="space-y-3">
      <div>
        <label className="text-xs dark:text-untold-muted block mb-1">SEO title</label>
        <input
          value={values.seo_title || ''}
          onChange={(e) => onChange({ ...values, seo_title: e.target.value })}
          className="w-full rounded-lg border dark:border-white/10 dark:bg-black/30 px-3 py-2 text-sm dark:text-white"
          placeholder="Documentary title for search & social"
        />
      </div>
      <div>
        <label className="text-xs dark:text-untold-muted block mb-1">SEO description</label>
        <textarea
          value={values.seo_description || ''}
          onChange={(e) => onChange({ ...values, seo_description: e.target.value })}
          rows={3}
          className="w-full rounded-lg border dark:border-white/10 dark:bg-black/30 px-3 py-2 text-sm dark:text-white resize-none"
          placeholder="Meta description (150–160 chars ideal)"
        />
      </div>
      <div>
        <label className="text-xs dark:text-untold-muted block mb-1">Keywords (comma-separated)</label>
        <input
          value={(values.seo_keywords || []).join(', ')}
          onChange={(e) => onChange({
            ...values,
            seo_keywords: e.target.value.split(',').map((s) => s.trim()).filter(Boolean),
          })}
          className="w-full rounded-lg border dark:border-white/10 dark:bg-black/30 px-3 py-2 text-sm dark:text-white"
          placeholder="documentary, sports, untold"
        />
      </div>
    </div>
  );
}
