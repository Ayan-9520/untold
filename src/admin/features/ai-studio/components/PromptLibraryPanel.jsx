import { useState } from 'react';
import { AI_MODULES } from '../constants';

export default function PromptLibraryPanel({ prompts, activeModule, onUse, onCreate, creating }) {
  const [title, setTitle] = useState('');
  const [template, setTemplate] = useState('');
  const [module, setModule] = useState(activeModule || 'research');

  const filtered = activeModule
    ? prompts.filter((p) => p.module === activeModule)
    : prompts;

  return (
    <div className="space-y-4">
      <form
        className="rounded-xl border dark:border-white/10 p-4 space-y-3"
        onSubmit={(e) => {
          e.preventDefault();
          if (!title.trim() || !template.trim()) return;
          onCreate({ title, module, prompt_template: template, tags: [module] });
          setTitle('');
          setTemplate('');
        }}
      >
        <p className="text-sm font-semibold dark:text-white">Save to library</p>
        <div className="grid gap-2 sm:grid-cols-2">
          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Prompt title"
            className="rounded-lg border dark:border-white/10 dark:bg-black/30 px-3 py-2 text-sm dark:text-white"
          />
          <select
            value={module}
            onChange={(e) => setModule(e.target.value)}
            className="rounded-lg border dark:border-white/10 dark:bg-black/30 px-3 py-2 text-sm dark:text-white"
          >
            {AI_MODULES.map((m) => (
              <option key={m.id} value={m.id}>{m.label}</option>
            ))}
          </select>
        </div>
        <textarea
          value={template}
          onChange={(e) => setTemplate(e.target.value)}
          rows={3}
          placeholder="Prompt template with {placeholders}"
          className="w-full rounded-lg border dark:border-white/10 dark:bg-black/30 px-3 py-2 text-sm dark:text-white font-mono"
        />
        <button type="submit" disabled={creating} className="text-xs text-untold-gold hover:underline disabled:opacity-50">
          Add prompt
        </button>
      </form>

      <ul className="space-y-2 max-h-[420px] overflow-y-auto">
        {filtered.map((p) => (
          <li key={p.id} className="rounded-lg border dark:border-white/10 px-3 py-2">
            <div className="flex items-start justify-between gap-2">
              <div className="min-w-0">
                <p className="text-sm font-medium dark:text-white">{p.title}</p>
                <p className="text-[10px] dark:text-untold-muted capitalize">{p.module}</p>
              </div>
              <button type="button" onClick={() => onUse(p)} className="text-xs text-untold-gold hover:underline shrink-0">
                Use
              </button>
            </div>
            <p className="text-xs dark:text-untold-muted mt-2 line-clamp-2 font-mono">{p.prompt_template}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}
