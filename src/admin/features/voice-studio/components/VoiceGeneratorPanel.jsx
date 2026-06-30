import { useEffect, useState } from 'react';
import { LANGUAGES, EMOTIONS } from '../constants';

export default function VoiceGeneratorPanel({
  overview,
  language,
  onLanguageChange,
  onGenerate,
  generating,
  previewing,
  onPreview,
  onTranslate,
  translating,
  initialText = '',
}) {
  const [text, setText] = useState(initialText);
  const [emotion, setEmotion] = useState('neutral');
  const [pitch, setPitch] = useState(1.0);
  const [speed, setSpeed] = useState(1.0);
  const [voiceId, setVoiceId] = useState('');
  const [translateTo, setTranslateTo] = useState('');
  const [syncSubtitles, setSyncSubtitles] = useState(true);
  const [provider, setProvider] = useState('');
  const [previewUrl, setPreviewUrl] = useState(null);
  const [translatedPreview, setTranslatedPreview] = useState('');

  const voices = overview?.voices_by_language?.[language] || [];

  useEffect(() => {
    if (voices.length && !voices.find((v) => v.id === voiceId)) {
      setVoiceId(voices[0].id);
    }
  }, [language, voices, voiceId]);

  const payload = () => ({
    text: text.trim(),
    language,
    emotion,
    pitch,
    speed,
    voice_id: voiceId || voices[0]?.id,
    translate_to: translateTo || undefined,
    sync_subtitles: syncSubtitles,
    provider: provider || undefined,
  });

  const handlePreview = async () => {
    if (!text.trim()) return;
    const result = await onPreview(payload());
    if (result?.audio_url) setPreviewUrl(result.audio_url);
  };

  const handleTranslate = async () => {
    if (!text.trim() || !translateTo) return;
    const result = await onTranslate({
      text: text.trim(),
      language,
      translate_to: translateTo,
    });
    if (result?.translated_text) setTranslatedPreview(result.translated_text);
  };

  return (
    <div className="space-y-5 max-w-2xl">
      <p className="text-sm dark:text-untold-muted">
        Generate narration with emotion, pitch, and speed controls. Subtitles sync automatically. Translation supported.
      </p>

      <div className="flex flex-wrap gap-2">
        {LANGUAGES.map((l) => (
          <button
            key={l.id}
            type="button"
            onClick={() => onLanguageChange(l.id)}
            className={`text-xs px-2 py-1 rounded-lg border ${
              language === l.id ? 'border-untold-gold bg-untold-gold/10 text-untold-gold' : 'dark:border-white/10 dark:text-untold-muted'
            }`}
          >
            {l.label}
          </button>
        ))}
      </div>

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
              } ${!p.available ? 'opacity-40' : ''}`}
            >
              {p.label}
            </button>
          ))}
        </div>
      )}

      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        rows={5}
        placeholder="Enter narration script…"
        className="w-full rounded-lg border dark:border-white/10 dark:bg-black/30 px-3 py-2 text-sm dark:text-white"
      />

      <div className="grid sm:grid-cols-2 gap-4">
        <label className="text-xs dark:text-untold-muted space-y-1 block">
          Voice
          <select
            value={voiceId}
            onChange={(e) => setVoiceId(e.target.value)}
            className="w-full rounded border dark:border-white/10 dark:bg-black/30 px-2 py-1.5 text-sm dark:text-white"
          >
            {voices.map((v) => <option key={v.id} value={v.id}>{v.label}</option>)}
          </select>
        </label>
        <label className="text-xs dark:text-untold-muted space-y-1 block">
          Emotion
          <select
            value={emotion}
            onChange={(e) => setEmotion(e.target.value)}
            className="w-full rounded border dark:border-white/10 dark:bg-black/30 px-2 py-1.5 text-sm dark:text-white"
          >
            {EMOTIONS.map((e) => <option key={e.id} value={e.id}>{e.label}</option>)}
          </select>
        </label>
      </div>

      <div className="grid sm:grid-cols-2 gap-4">
        <label className="text-xs dark:text-untold-muted space-y-1 block">
          Pitch — {pitch.toFixed(1)}×
          <input type="range" min="0.5" max="2" step="0.1" value={pitch} onChange={(e) => setPitch(Number(e.target.value))} className="w-full" />
        </label>
        <label className="text-xs dark:text-untold-muted space-y-1 block">
          Speed — {speed.toFixed(1)}×
          <input type="range" min="0.5" max="2" step="0.1" value={speed} onChange={(e) => setSpeed(Number(e.target.value))} className="w-full" />
        </label>
      </div>

      <div className="flex flex-wrap gap-3 items-center text-xs">
        <label className="dark:text-untold-muted flex items-center gap-2">
          Translate to
          <select
            value={translateTo}
            onChange={(e) => setTranslateTo(e.target.value)}
            className="rounded border dark:border-white/10 dark:bg-black/30 px-2 py-1 text-sm dark:text-white"
          >
            <option value="">None</option>
            {LANGUAGES.filter((l) => l.id !== language).map((l) => (
              <option key={l.id} value={l.id}>{l.label}</option>
            ))}
          </select>
        </label>
        <label className="dark:text-untold-muted flex items-center gap-2">
          <input type="checkbox" checked={syncSubtitles} onChange={(e) => setSyncSubtitles(e.target.checked)} />
          Sync subtitles
        </label>
      </div>

      {translatedPreview && (
        <div className="rounded-lg border dark:border-white/10 p-3 text-xs dark:text-untold-muted">
          <p className="text-[10px] uppercase tracking-wide text-untold-gold mb-1">Translation preview</p>
          {translatedPreview}
        </div>
      )}

      {previewUrl && (
        <audio controls src={previewUrl} className="w-full" />
      )}

      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          disabled={!text.trim() || previewing}
          onClick={handlePreview}
          className="px-3 py-2 text-sm rounded-lg border dark:border-white/10 dark:text-white disabled:opacity-50"
        >
          {previewing ? 'Previewing…' : 'Preview'}
        </button>
        {translateTo && (
          <button
            type="button"
            disabled={!text.trim() || translating}
            onClick={handleTranslate}
            className="px-3 py-2 text-sm rounded-lg border dark:border-white/10 dark:text-white disabled:opacity-50"
          >
            {translating ? 'Translating…' : 'Translate text'}
          </button>
        )}
        <button
          type="button"
          disabled={!text.trim() || generating}
          onClick={() => onGenerate(payload())}
          className="px-4 py-2 text-sm rounded-lg bg-untold-gold text-black font-semibold disabled:opacity-50"
        >
          {generating ? 'Queuing…' : 'Generate narration'}
        </button>
      </div>
    </div>
  );
}
