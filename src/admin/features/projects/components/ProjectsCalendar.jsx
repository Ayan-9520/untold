import { Link } from 'react-router-dom';
import { studioPath } from '../../../../config/ecosystem';
import StageBadge from './StageBadge';

function monthRange(date = new Date()) {
  const start = new Date(date.getFullYear(), date.getMonth(), 1);
  const end = new Date(date.getFullYear(), date.getMonth() + 1, 0);
  return { start, end, days: end.getDate(), month: start.toLocaleString('default', { month: 'long', year: 'numeric' }) };
}

export default function ProjectsCalendar({ feed, monthDate, onMonthChange }) {
  const { start, days, month } = monthRange(monthDate);
  const startDow = start.getDay();

  const itemsByDay = {};
  const addItem = (day, item) => {
    if (!itemsByDay[day]) itemsByDay[day] = [];
    itemsByDay[day].push(item);
  };

  (feed?.projects || []).forEach((p) => {
    if (!p.due_date) return;
    const d = new Date(p.due_date);
    if (d.getMonth() === monthDate.getMonth() && d.getFullYear() === monthDate.getFullYear()) {
      addItem(d.getDate(), { type: 'project', data: p });
    }
  });
  (feed?.tasks || []).forEach((t) => {
    if (!t.due_date) return;
    const d = new Date(t.due_date);
    if (d.getMonth() === monthDate.getMonth() && d.getFullYear() === monthDate.getFullYear()) {
      addItem(d.getDate(), { type: 'task', data: t });
    }
  });
  (feed?.events || []).forEach((e) => {
    const d = new Date(e.start_at);
    if (d.getMonth() === monthDate.getMonth() && d.getFullYear() === monthDate.getFullYear()) {
      addItem(d.getDate(), { type: 'event', data: e });
    }
  });

  const cells = [];
  for (let i = 0; i < startDow; i++) cells.push(null);
  for (let d = 1; d <= days; d++) cells.push(d);

  const prev = () => onMonthChange(new Date(monthDate.getFullYear(), monthDate.getMonth() - 1, 1));
  const next = () => onMonthChange(new Date(monthDate.getFullYear(), monthDate.getMonth() + 1, 1));

  return (
    <div className="rounded-xl border dark:border-white/10 light:border-gray-200 overflow-hidden">
      <div className="flex items-center justify-between px-4 py-3 border-b dark:border-white/10 light:border-gray-200 dark:bg-untold-card/30">
        <button type="button" onClick={prev} className="text-sm text-untold-gold">←</button>
        <h3 className="text-sm font-semibold dark:text-white light:text-black">{month}</h3>
        <button type="button" onClick={next} className="text-sm text-untold-gold">→</button>
      </div>
      <div className="grid grid-cols-7 text-[10px] uppercase tracking-wider dark:text-untold-muted border-b dark:border-white/10">
        {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((d) => (
          <div key={d} className="px-2 py-2 text-center font-medium">{d}</div>
        ))}
      </div>
      <div className="grid grid-cols-7 auto-rows-fr min-h-[320px]">
        {cells.map((day, i) => (
          <div
            key={i}
            className={`border-b border-r dark:border-white/5 light:border-gray-100 p-1 min-h-[72px] ${
              day ? '' : 'dark:bg-black/10 light:bg-gray-50/50'
            }`}
          >
            {day && (
              <>
                <span className="text-[10px] dark:text-untold-muted">{day}</span>
                <div className="space-y-0.5 mt-0.5">
                  {(itemsByDay[day] || []).slice(0, 3).map((item, idx) => (
                    item.type === 'project' ? (
                      <Link
                        key={idx}
                        to={studioPath(`projects/${item.data.id}`)}
                        className="block text-[9px] truncate rounded px-1 py-0.5 bg-untold-gold/15 text-untold-gold"
                      >
                        {item.data.title}
                      </Link>
                    ) : (
                      <span key={idx} className="block text-[9px] truncate rounded px-1 py-0.5 bg-blue-500/15 text-blue-400">
                        {item.data.title}
                      </span>
                    )
                  ))}
                </div>
              </>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
