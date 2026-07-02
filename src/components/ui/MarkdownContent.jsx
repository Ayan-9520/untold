function renderMarkdown(md) {
  if (!md) return '';
  return md
    .split('\n')
    .map((line) => {
      if (line.startsWith('# ')) return `<h1 class="legal-h1">${line.slice(2)}</h1>`;
      if (line.startsWith('## ')) return `<h2 class="legal-h2">${line.slice(3)}</h2>`;
      if (line.startsWith('- ')) return `<li>${line.slice(2)}</li>`;
      if (!line.trim()) return '';
      return `<p class="legal-p">${line}</p>`;
    })
    .join('');
}

export default function MarkdownContent({ content }) {
  const html = renderMarkdown(content);
  return (
    <div
      className="legal-content prose-invert max-w-none"
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}
