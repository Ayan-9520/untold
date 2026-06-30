function downloadBlob(filename, blob) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

export default function ExportMenu({ scriptId, title, onExportMarkdown, onExportPdf, onExportWord }) {
  const safeName = (title || 'script').replace(/\s+/g, '-').slice(0, 40);

  return (
    <div className="flex flex-wrap gap-2">
      <button
        type="button"
        onClick={async () => {
          const md = await onExportMarkdown(scriptId);
          downloadBlob(`${safeName}.md`, new Blob([md], { type: 'text/markdown' }));
        }}
        className="px-3 py-1.5 text-xs rounded-lg border dark:border-white/10 text-untold-gold hover:border-untold-gold/40"
      >
        Markdown
      </button>
      <button
        type="button"
        onClick={() => onExportPdf(scriptId, safeName)}
        className="px-3 py-1.5 text-xs rounded-lg border dark:border-white/10 text-untold-gold hover:border-untold-gold/40"
      >
        PDF
      </button>
      <button
        type="button"
        onClick={async () => {
          const doc = await onExportWord(scriptId);
          downloadBlob(`${safeName}.doc`, new Blob([doc], { type: 'application/msword' }));
        }}
        className="px-3 py-1.5 text-xs rounded-lg border dark:border-white/10 text-untold-gold hover:border-untold-gold/40"
      >
        Word
      </button>
    </div>
  );
}
