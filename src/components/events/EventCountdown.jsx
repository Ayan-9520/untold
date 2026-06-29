import useCountdown from '../../hooks/useCountdown';

function Unit({ value, label }) {
  return (
    <div className="flex flex-col items-center min-w-[3rem] sm:min-w-[3.5rem]">
      <span className="font-display text-xl sm:text-2xl font-bold tabular-nums dark:text-untold-white light:text-black">
        {String(value).padStart(2, '0')}
      </span>
      <span className="text-[10px] sm:text-xs uppercase tracking-wider dark:text-untold-muted light:text-gray-500 mt-0.5">
        {label}
      </span>
    </div>
  );
}

export default function EventCountdown({ targetDate, compact = false }) {
  const { days, hours, minutes, seconds, expired } = useCountdown(targetDate);

  if (expired) {
    return (
      <span className={`font-medium text-untold-gold ${compact ? 'text-xs' : 'text-sm'}`}>
        Starting soon
      </span>
    );
  }

  return (
    <div className={`flex items-center gap-2 sm:gap-3 ${compact ? '' : 'px-3 py-2 rounded-lg dark:bg-white/5 light:bg-black/5'}`}>
      {days > 0 && <Unit value={days} label="Days" />}
      <Unit value={hours} label="Hrs" />
      <Unit value={minutes} label="Min" />
      {!compact && <Unit value={seconds} label="Sec" />}
    </div>
  );
}
