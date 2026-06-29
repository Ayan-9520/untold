export default function MatchTimeline({ timeline = [] }) {
  if (timeline.length === 0) return null;

  const typeColors = {
    goal: 'bg-green-500',
    wicket: 'bg-red-500',
    six: 'bg-untold-gold',
    point: 'bg-blue-500',
    lap: 'bg-purple-500',
    knockout: 'bg-red-600',
    default: 'bg-gray-500',
  };

  return (
    <div className="rounded-xl border dark:border-untold-border light:border-gray-200 p-4 sm:p-6">
      <h2 className="font-semibold dark:text-untold-white light:text-black mb-4">Match Timeline</h2>
      <ol className="relative border-l-2 dark:border-untold-border light:border-gray-200 ml-3 space-y-4">
        {timeline.map((item) => (
          <li key={item.id} className="ml-6 relative">
            <span
              className={`absolute -left-[1.65rem] top-1 w-3 h-3 rounded-full ring-4 ring-untold-dark light:ring-white
                ${typeColors[item.type] || typeColors.default}`}
            />
            <p className="text-xs font-bold text-untold-gold">{item.minute}</p>
            <p className="text-sm font-semibold dark:text-untold-white light:text-black">{item.label}</p>
            <p className="text-xs dark:text-untold-muted light:text-gray-500 mt-0.5">{item.detail}</p>
          </li>
        ))}
      </ol>
    </div>
  );
}
