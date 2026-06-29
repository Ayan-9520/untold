import Badge from '../ui/Badge';

export default function AICommentaryFeed({ commentary = [], title = 'AI Commentary', limit }) {
  const items = limit ? commentary.slice(0, limit) : commentary;

  if (items.length === 0) {
    return (
      <div className="rounded-xl border dark:border-untold-border light:border-gray-200 p-6 text-center">
        <p className="text-sm dark:text-untold-muted light:text-gray-500">Commentary will appear as the match progresses.</p>
      </div>
    );
  }

  return (
    <div id="commentary" className="rounded-xl border dark:border-untold-border light:border-gray-200 overflow-hidden">
      <div className="px-4 py-3 border-b dark:border-untold-border light:border-gray-200 dark:bg-untold-surface/50 light:bg-gray-50 flex items-center justify-between">
        <h2 className="font-semibold dark:text-untold-white light:text-black">{title}</h2>
        <Badge variant="premium" size="sm">AI Powered</Badge>
      </div>
      <ul className="divide-y dark:divide-untold-border light:divide-gray-200 max-h-[480px] overflow-y-auto">
        {items.map((item) => (
          <li key={item.id} className="px-4 py-3 hover:dark:bg-white/5 hover:light:bg-gray-50 transition-colors animate-fade-in">
            <div className="flex gap-3">
              <span className="shrink-0 text-xs font-bold text-untold-gold w-12">{item.minute || item.time}</span>
              <div>
                {item.type && item.type !== 'update' && item.type !== 'default' && (
                  <span className="text-[10px] font-bold uppercase text-red-400 mr-2">{item.type}</span>
                )}
                <p className="text-sm dark:text-untold-white light:text-gray-800 leading-relaxed">{item.text}</p>
              </div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
