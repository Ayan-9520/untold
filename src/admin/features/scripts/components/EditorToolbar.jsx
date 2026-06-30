import { useRef, useCallback } from 'react';

const COMMANDS = [
  { cmd: 'bold', label: 'B', title: 'Bold', className: 'font-bold' },
  { cmd: 'italic', label: 'I', title: 'Italic', className: 'italic' },
  { cmd: 'underline', label: 'U', title: 'Underline', className: 'underline' },
  { cmd: 'insertUnorderedList', label: '•', title: 'Bullet list' },
  { cmd: 'insertOrderedList', label: '1.', title: 'Numbered list' },
];

const BLOCKS = [
  { value: 'h1', label: 'H1' },
  { value: 'h2', label: 'H2' },
  { value: 'h3', label: 'H3' },
  { value: 'p', label: 'P' },
];

export default function EditorToolbar({ onCommand, onBlock }) {
  return (
    <div className="flex flex-wrap gap-1 p-2 border-b dark:border-white/10 dark:bg-black/20 rounded-t-lg">
      {COMMANDS.map((c) => (
        <button
          key={c.cmd}
          type="button"
          title={c.title}
          onMouseDown={(e) => {
            e.preventDefault();
            onCommand(c.cmd);
          }}
          className={`px-2 py-1 text-xs rounded border dark:border-white/10 hover:border-untold-gold/40 dark:text-white min-w-[28px] ${c.className || ''}`}
        >
          {c.label}
        </button>
      ))}
      <span className="w-px h-6 bg-white/10 mx-1 self-center" />
      {BLOCKS.map((b) => (
        <button
          key={b.value}
          type="button"
          onMouseDown={(e) => {
            e.preventDefault();
            onBlock(b.value);
          }}
          className="px-2 py-1 text-xs rounded border dark:border-white/10 hover:border-untold-gold/40 dark:text-untold-muted"
        >
          {b.label}
        </button>
      ))}
    </div>
  );
}

export function useRichTextCommands(editorRef) {
  const exec = useCallback((cmd, value = null) => {
    editorRef.current?.focus();
    document.execCommand(cmd, false, value);
  }, [editorRef]);

  const setBlock = useCallback((tag) => {
    editorRef.current?.focus();
    document.execCommand('formatBlock', false, tag);
  }, [editorRef]);

  return { exec, setBlock };
}
