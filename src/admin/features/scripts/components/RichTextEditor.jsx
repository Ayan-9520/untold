import { useRef, useEffect, useCallback } from 'react';
import EditorToolbar, { useRichTextCommands } from './EditorToolbar';

export default function RichTextEditor({ value, onChange, placeholder = 'Start writing…', minHeight = 420 }) {
  const editorRef = useRef(null);
  const lastValue = useRef(value);
  const { exec, setBlock } = useRichTextCommands(editorRef);

  useEffect(() => {
    if (editorRef.current && value !== lastValue.current) {
      editorRef.current.innerHTML = value || '';
      lastValue.current = value;
    }
  }, [value]);

  const handleInput = useCallback(() => {
    const html = editorRef.current?.innerHTML || '';
    lastValue.current = html;
    onChange(html);
  }, [onChange]);

  return (
    <div className="script-rich-editor rounded-lg border dark:border-white/10 overflow-hidden">
      <EditorToolbar onCommand={exec} onBlock={setBlock} />
      <div
        ref={editorRef}
        contentEditable
        suppressContentEditableWarning
        onInput={handleInput}
        data-placeholder={placeholder}
        className="script-rich-editor__body px-4 py-3 text-sm dark:text-white leading-relaxed outline-none overflow-y-auto"
        style={{ minHeight }}
      />
    </div>
  );
}
