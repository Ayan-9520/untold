import { useState } from 'react';
import ProviderSelect from './ProviderSelect';

export default function ModulePanel({ module, providers, onGenerate, generating, initialPrompt = '' }) {
  const [prompt, setPrompt] = useState(initialPrompt);
  const [provider, setProvider] = useState('');
  const [targetLanguage, setTargetLanguage] = useState('es');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!prompt.trim()) return;
    const parameters = module.id === 'translation' ? { target_language: targetLanguage } : {};
    onGenerate({
      module: module.id,
      prompt: prompt.trim(),
      provider: provider || null,
      parameters,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 max-w-2xl">
      <div>
        <h3 className="text-lg font-semibold dark:text-white">{module.label}</h3>
        <p className="text-sm dark:text-untold-muted mt-1">{module.description}</p>
      </div>
      <label className="block space-y-1">
        <span className="text-[10px] uppercase tracking-wider dark:text-untold-muted">Provider</span>
        <ProviderSelect
          providers={providers}
          value={provider}
          onChange={setProvider}
          moduleId={module.id}
        />
      </label>
      {module.id === 'translation' && (
        <label className="block space-y-1">
          <span className="text-[10px] uppercase tracking-wider dark:text-untold-muted">Target language</span>
          <select
            value={targetLanguage}
            onChange={(e) => setTargetLanguage(e.target.value)}
            className="w-full rounded-lg border dark:border-white/10 dark:bg-black/30 px-3 py-2 text-sm dark:text-white"
          >
            {['es', 'fr', 'de', 'hi', 'ar', 'pt', 'ja'].map((l) => (
              <option key={l} value={l}>{l.toUpperCase()}</option>
            ))}
          </select>
        </label>
      )}
      <label className="block space-y-1">
        <span className="text-[10px] uppercase tracking-wider dark:text-untold-muted">Prompt</span>
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          rows={6}
          required
          placeholder={`Describe what ${module.label} should generate…`}
          className="w-full rounded-lg border dark:border-white/10 dark:bg-black/30 px-3 py-2 text-sm dark:text-white font-mono"
        />
      </label>
      <button
        type="submit"
        disabled={generating || !prompt.trim()}
        className="px-4 py-2 text-sm rounded-lg bg-untold-gold text-black font-medium disabled:opacity-50"
      >
        {generating ? 'Queuing…' : 'Generate'}
      </button>
    </form>
  );
}
