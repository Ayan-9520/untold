import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useWebAuth } from '../../context/WebAuthContext';
import viewerApi from '../../api/viewer';

export default function LiveSchedule({ matches = [] }) {
  const { t } = useTranslation();
  const { isAuthenticated } = useWebAuth();
  const [reminders, setReminders] = useState([]);

  useEffect(() => {
    if (isAuthenticated) {
      viewerApi.listReminders().then(setReminders).catch(() => setReminders([]));
    }
  }, [isAuthenticated]);

  const reminderIds = new Set(reminders.map((r) => r.match_id));

  const toggleReminder = async (match) => {
    if (!isAuthenticated) {
      window.location.href = '/login';
      return;
    }
    const id = String(match.id);
    if (reminderIds.has(id)) {
      await viewerApi.removeReminder(id);
      setReminders((prev) => prev.filter((r) => r.match_id !== id));
    } else {
      const row = await viewerApi.setReminder({
        match_id: id,
        match_title: match.title || `${match.team_a} vs ${match.team_b}`,
        starts_at: match.starts_at || null,
      });
      setReminders((prev) => [...prev, row]);
    }
  };

  if (!matches.length) return null;

  return (
    <section className="py-8">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <h2 className="font-display text-xl font-bold text-white mb-4">{t('live.schedule')}</h2>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {matches.slice(0, 9).map((match) => {
            const id = String(match.id);
            const reminded = reminderIds.has(id);
            return (
              <div key={id} className="rounded-xl border dark:border-untold-border p-4 flex justify-between items-start gap-3">
                <div>
                  <p className="text-xs text-untold-gold uppercase">{match.sport}</p>
                  <p className="text-sm font-semibold text-white mt-1">
                    {match.title || `${match.team_a || match.home} vs ${match.team_b || match.away}`}
                  </p>
                  <p className="text-xs text-untold-muted mt-1">{match.status || 'Scheduled'}</p>
                </div>
                <button
                  type="button"
                  onClick={() => toggleReminder(match)}
                  className={`shrink-0 text-xs px-2 py-1 rounded-full border ${reminded ? 'border-untold-gold text-untold-gold' : 'border-untold-border text-untold-muted'}`}
                >
                  {reminded ? t('live.reminded') : t('live.remindMe')}
                </button>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
