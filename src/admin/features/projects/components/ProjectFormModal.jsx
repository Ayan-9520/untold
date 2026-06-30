import { useState, useEffect } from 'react';
import { PROJECT_STAGES, STAGE_LABELS } from '../constants';

const EMPTY = {
  title: '',
  description: '',
  category: '',
  stage: 'research',
  assignee: '',
  tags: '',
  due_date: '',
};

export default function ProjectFormModal({ open, onClose, onSubmit, initial, loading }) {
  const [form, setForm] = useState(EMPTY);

  useEffect(() => {
    if (!open) return;
    if (initial) {
      setForm({
        title: initial.title || '',
        description: initial.description || '',
        category: initial.category || '',
        stage: initial.stage || 'research',
        assignee: initial.assignee || '',
        tags: (initial.tags || []).join(', '),
        due_date: initial.due_date ? initial.due_date.slice(0, 10) : '',
      });
    } else {
      setForm(EMPTY);
    }
  }, [open, initial]);

  if (!open) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({
      title: form.title.trim(),
      description: form.description.trim() || null,
      category: form.category.trim() || null,
      stage: form.stage,
      assignee: form.assignee.trim() || null,
      tags: form.tags.split(',').map((t) => t.trim()).filter(Boolean),
      due_date: form.due_date ? new Date(form.due_date).toISOString() : null,
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70" role="dialog">
      <div className="w-full max-w-lg rounded-xl border dark:border-white/10 light:border-gray-200 dark:bg-untold-surface light:bg-white p-6 shadow-xl max-h-[90vh] overflow-y-auto">
        <h2 className="text-lg font-semibold dark:text-white light:text-black mb-4">
          {initial ? 'Edit Project' : 'Create Project'}
        </h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <label className="block">
            <span className="text-xs font-medium dark:text-untold-muted light:text-gray-500">Title *</span>
            <input
              required
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
              className="mt-1 w-full rounded-lg border dark:border-white/10 light:border-gray-300 dark:bg-black/30 light:bg-gray-50 px-3 py-2 text-sm dark:text-white light:text-black"
            />
          </label>
          <label className="block">
            <span className="text-xs font-medium dark:text-untold-muted light:text-gray-500">Description</span>
            <textarea
              rows={3}
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              className="mt-1 w-full rounded-lg border dark:border-white/10 light:border-gray-300 dark:bg-black/30 light:bg-gray-50 px-3 py-2 text-sm dark:text-white light:text-black"
            />
          </label>
          <div className="grid grid-cols-2 gap-3">
            <label className="block">
              <span className="text-xs font-medium dark:text-untold-muted light:text-gray-500">Stage</span>
              <select
                value={form.stage}
                onChange={(e) => setForm({ ...form, stage: e.target.value })}
                className="mt-1 w-full rounded-lg border dark:border-white/10 light:border-gray-300 dark:bg-black/30 light:bg-gray-50 px-3 py-2 text-sm dark:text-white light:text-black"
              >
                {PROJECT_STAGES.map((s) => (
                  <option key={s} value={s}>{STAGE_LABELS[s]}</option>
                ))}
              </select>
            </label>
            <label className="block">
              <span className="text-xs font-medium dark:text-untold-muted light:text-gray-500">Due date</span>
              <input
                type="date"
                value={form.due_date}
                onChange={(e) => setForm({ ...form, due_date: e.target.value })}
                className="mt-1 w-full rounded-lg border dark:border-white/10 light:border-gray-300 dark:bg-black/30 light:bg-gray-50 px-3 py-2 text-sm dark:text-white light:text-black"
              />
            </label>
          </div>
          <label className="block">
            <span className="text-xs font-medium dark:text-untold-muted light:text-gray-500">Assignee</span>
            <input
              value={form.assignee}
              onChange={(e) => setForm({ ...form, assignee: e.target.value })}
              className="mt-1 w-full rounded-lg border dark:border-white/10 light:border-gray-300 dark:bg-black/30 light:bg-gray-50 px-3 py-2 text-sm dark:text-white light:text-black"
            />
          </label>
          <label className="block">
            <span className="text-xs font-medium dark:text-untold-muted light:text-gray-500">Tags (comma-separated)</span>
            <input
              value={form.tags}
              onChange={(e) => setForm({ ...form, tags: e.target.value })}
              placeholder="documentary, sports, viral"
              className="mt-1 w-full rounded-lg border dark:border-white/10 light:border-gray-300 dark:bg-black/30 light:bg-gray-50 px-3 py-2 text-sm dark:text-white light:text-black"
            />
          </label>
          <div className="flex justify-end gap-2 pt-2">
            <button type="button" onClick={onClose} className="px-4 py-2 text-sm rounded-lg dark:text-untold-muted light:text-gray-600">
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 text-sm font-semibold rounded-lg bg-untold-gold text-black disabled:opacity-50"
            >
              {loading ? 'Saving…' : initial ? 'Save changes' : 'Create project'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
