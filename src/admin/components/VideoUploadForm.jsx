import { useState } from 'react';
import { videos, aiPipeline } from '../api/adminApi';
import { UploadIcon } from './AdminIcons';

export default function VideoUploadForm({ categories, onSuccess, onCancel, defaultType = 'documentary', defaultCategorySlug }) {
  const defaultCategory = categories.find((c) => c.slug === defaultCategorySlug);
  const [form, setForm] = useState({
    title: '',
    slug: '',
    description: '',
    category_id: defaultCategory?.id?.toString() || '',
    duration: '',
    year: new Date().getFullYear(),
    rating: 'TV-MA',
    image_url: '',
    hero_image_url: '',
    video_url: '',
    transcript: '',
    video_type: defaultType,
    is_featured: false,
    is_trending: false,
    trigger_ai_localization: true,
    target_languages: ['hi', 'es', 'ru', 'ar'],
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
      ...(name === 'title' && !prev.slug
        ? { slug: value.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '') }
        : {}),
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const created = await videos.create({
        ...form,
        category_id: form.category_id ? Number(form.category_id) : null,
        year: Number(form.year),
      });
      if (form.trigger_ai_localization) {
        await aiPipeline.createJob({
          video_id: created.id,
          video_title: form.title,
          source_language: 'en',
          target_languages: form.target_languages,
          transcript: form.transcript || null,
        }).catch(() => {});
      }
      onSuccess();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to upload video');
    } finally {
      setLoading(false);
    }
  };

  const inputClass = `w-full rounded-lg px-3 py-2.5 text-sm border outline-none
    dark:bg-untold-dark dark:border-white/10 dark:text-untold-white
    light:bg-gray-50 light:border-gray-200 light:text-black
    focus:ring-2 focus:ring-untold-gold/40`;

  const fields = [
    { name: 'title', label: 'Title', required: true },
    { name: 'slug', label: 'Slug', required: true },
    { name: 'description', label: 'Description', type: 'textarea' },
    { name: 'duration', label: 'Duration (e.g. 1h 8m)' },
    { name: 'image_url', label: 'Thumbnail URL' },
    { name: 'hero_image_url', label: 'Hero Image URL' },
    { name: 'video_url', label: 'Video Stream URL' },
    { name: 'transcript', label: 'Transcript (optional — AI uses for localization)', type: 'textarea' },
  ];

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="flex items-center gap-3 p-4 rounded-xl dark:bg-untold-gold/5 border border-dashed border-untold-gold/30">
        <UploadIcon className="w-8 h-8 text-untold-gold" />
        <div>
          <p className="text-sm font-medium dark:text-untold-white light:text-black">Add new content</p>
          <p className="text-xs dark:text-untold-muted light:text-gray-500">Fill in metadata to publish to the platform</p>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {fields.map((f) => (
          <div key={f.name} className={f.type === 'textarea' ? 'sm:col-span-2' : ''}>
            <label className="block text-xs font-medium dark:text-untold-muted light:text-gray-500 mb-1">
              {f.label}
            </label>
            {f.type === 'textarea' ? (
              <textarea name={f.name} value={form[f.name]} onChange={handleChange} rows={3} className={`${inputClass} resize-none`} />
            ) : (
              <input name={f.name} value={form[f.name]} onChange={handleChange} required={f.required} className={inputClass} />
            )}
          </div>
        ))}

        <div>
          <label className="block text-xs font-medium dark:text-untold-muted light:text-gray-500 mb-1">Category</label>
          <select name="category_id" value={form.category_id} onChange={handleChange} className={inputClass}>
            <option value="">Select category</option>
            {categories.map((c) => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-xs font-medium dark:text-untold-muted light:text-gray-500 mb-1">Type</label>
          <select name="video_type" value={form.video_type} onChange={handleChange} className={inputClass}>
            <option value="documentary">Documentary</option>
            <option value="short">Short</option>
            <option value="series">Series</option>
          </select>
        </div>

        <div>
          <label className="block text-xs font-medium dark:text-untold-muted light:text-gray-500 mb-1">Year</label>
          <input name="year" type="number" value={form.year} onChange={handleChange} className={inputClass} />
        </div>

        <div>
          <label className="block text-xs font-medium dark:text-untold-muted light:text-gray-500 mb-1">Rating</label>
          <input name="rating" value={form.rating} onChange={handleChange} className={inputClass} />
        </div>
      </div>

      <div className="flex gap-4 flex-wrap">
        <label className="flex items-center gap-2 text-sm dark:text-untold-white light:text-black">
          <input type="checkbox" name="is_featured" checked={form.is_featured} onChange={handleChange} className="rounded" />
          Featured
        </label>
        <label className="flex items-center gap-2 text-sm dark:text-untold-white light:text-black">
          <input type="checkbox" name="is_trending" checked={form.is_trending} onChange={handleChange} className="rounded" />
          Trending
        </label>
        <label className="flex items-center gap-2 text-sm dark:text-untold-white light:text-black">
          <input type="checkbox" name="trigger_ai_localization" checked={form.trigger_ai_localization} onChange={handleChange} className="rounded" />
          Trigger AI Localization
        </label>
      </div>

      {error && <p className="text-sm text-red-400">{typeof error === 'string' ? error : JSON.stringify(error)}</p>}

      <div className="flex gap-3 pt-2">
        <button type="button" onClick={onCancel} className="flex-1 py-2.5 rounded-lg text-sm dark:bg-white/5 light:bg-gray-100">
          Cancel
        </button>
        <button
          type="submit"
          disabled={loading}
          className="flex-1 py-2.5 rounded-lg bg-untold-gold text-untold-dark text-sm font-semibold disabled:opacity-60"
        >
          {loading ? 'Publishing...' : 'Publish Video'}
        </button>
      </div>
    </form>
  );
}
