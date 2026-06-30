export default function VoicePromptLibrary({ prompts, language, onUse }) {
  const filtered = prompts?.filter((p) => {
    if (!language) return true;
    const lang = p.parameters?.language;
    return !lang || lang === language;
  }) || [];

  if (!filtered.length) {
    return <p className="text-sm dark:text-untold-muted">No narration prompts for this language yet.</p>;
  }

  return (
    <ul className="space-y-2 max-h-96 overflow-y-auto">
      {filtered.map((p) => (
        <li key={p.id} className="rounded-lg border dark:border-white/10 px-3 py-2">
          <p className="text-sm font-medium dark:text-white">{p.title}</p>
          {p.description && <p className="text-[10px] dark:text-untold-muted mt-0.5">{p.description}</p>}
          <button type="button" onClick={() => onUse(p)} className="text-xs text-untold-gold mt-2 hover:underline">
            Use script →
          </button>
        </li>
      ))}
    </ul>
  );
}
