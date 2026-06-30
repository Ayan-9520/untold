import { useState } from 'react';
import { CONTENT_TYPES } from '../constants';

export default function TranslationGeneratorPanel({ overview, onTranslate, translating, projectId }) {
  const [sourceText, setSourceText] = useState('');
  const [contentType, setContentType] = useState('script');
  const [sourceLang, setSourceLang] = useState('en');
  const [targetLang, setTargetLang] = useState('es');
  const [autoSync, setAutoSync] = useState(true);
  const [generateSrt, setGenerateSrt] = useState(true);
  const [generateVtt, setGenerateVtt] = useState(true);
  const [provider, setProvider] = useState('');

  const languages = overview?.languages || [];

  return (
    <div className="space-y-5 max-w-2xl">
      <p className="text-sm dark:text-untold-muted">
        Translate scripts, voice narration, subtitles, metadata, descriptions, and titles across 10 languages.
        Generates SRT/VTT with auto-sync and uses translation memory for faster repeat work.
      </p>
      {overview?.providers?.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {overview.providers.map((p) => (
            <button
              key={p.id}
              type="button"
              disabled={!p.available}
              onClick={() => setProvider(p.id)}
              className={`text-[10px] px-2 py-1 rounded-full border ${
                provider === p.id ? 'border-untold-gold text-untold-gold' : 'dark:border-white/10 dark:text-untold-muted'
              }`}
            >
              {p.label}
            </button>
          ))}
        </div>
      )}
      <textarea
        value={sourceText}
        onChange={(e) => setSourceText(e.target.value)}
        rows={6}
        placeholder="Paste script, subtitle cues, title, description, or metadata to translate…"
        className="w-full rounded-lg border dark:border-white/10 dark:bg-black/30 px-3 py-2 text-sm dark:text-white font-mono"
      />
      <div className="grid sm:grid-cols-2 gap-4">
        <label className="text-xs dark:text-untold-muted block">
          Content type
          <select
            value={contentType}
            onChange={(e) => setContentType(e.target.value)}
            className="w-full mt-1 rounded border dark:border-white/10 dark:bg-black/30 px-2 py-1.5 text-sm dark:text-white"
          >
            {CONTENT_TYPES.map((c) => (
              <option key={c.id} value={c.id}>{c.label}</option>
            ))}
          </select>
        </label>
        <label className="text-xs dark:text-untold-muted block">
          Source language
          <select
            value={sourceLang}
            onChange={(e) => setSourceLang(e.target.value)}
            className="w-full mt-1 rounded border dark:border-white/10 dark:bg-black/30 px-2 py-1.5 text-sm dark:text-white"
          >
            {languages.map((l) => (
              <option key={l.code} value={l.code}>{l.label}</option>
            ))}
          </select>
        </label>
        <label className="text-xs dark:text-untold-muted block">
          Target language
          <select
            value={targetLang}
            onChange={(e) => setTargetLang(e.target.value)}
            className="w-full mt-1 rounded border dark:border-white/10 dark:bg-black/30 px-2 py-1.5 text-sm dark:text-white"
          >
            {languages.filter((l) => l.code !== sourceLang).map((l) => (
              <option key={l.code} value={l.code}>{l.label}</option>
            ))}
          </select>
        </label>
      </div>
      <div className="flex flex-wrap gap-4 text-xs dark:text-untold-muted">
        <label className="flex items-center gap-2 cursor-pointer">
          <input type="checkbox" checked={autoSync} onChange={(e) => setAutoSync(e.target.checked)} />
          Auto-sync timing
        </label>
        <label className="flex items-center gap-2 cursor-pointer">
          <input type="checkbox" checked={generateSrt} onChange={(e) => setGenerateSrt(e.target.checked)} />
          Generate SRT
        </label>
        <label className="flex items-center gap-2 cursor-pointer">
          <input type="checkbox" checked={generateVtt} onChange={(e) => setGenerateVtt(e.target.checked)} />
          Generate VTT
        </label>
      </div>
      <button
        type="button"
        disabled={!sourceText.trim() || translating || sourceLang === targetLang}
        onClick={() => onTranslate({
          source_text: sourceText.trim(),
          content_type: contentType,
          source_lang: sourceLang,
          target_lang: targetLang,
          auto_sync: autoSync,
          generate_srt: generateSrt,
          generate_vtt: generateVtt,
          project_id: projectId || undefined,
          provider: provider || undefined,
        })}
        className="px-4 py-2 text-sm rounded-lg bg-untold-gold text-black font-semibold disabled:opacity-50"
      >
        {translating ? 'Queuing…' : 'Translate'}
      </button>
    </div>
  );
}
