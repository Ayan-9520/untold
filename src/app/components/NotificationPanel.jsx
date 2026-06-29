import { useState, useEffect } from 'react';
import { useAppUI } from '../context/AppUIContext';
import { appApi } from '../../api/appApi';
import { CloseIcon } from '../../components/icons';

export default function NotificationPanel() {
  const { notificationsOpen, closeNotifications } = useAppUI();
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    if (notificationsOpen) {
      appApi.getNotifications().then(({ data }) => setNotifications(data));
    }
  }, [notificationsOpen]);

  if (!notificationsOpen) return null;

  const unread = notifications.filter((n) => !n.read).length;

  return (
    <div className="fixed inset-0 z-50 mx-auto max-w-[430px] animate-fade-in">
      <div
        className="absolute inset-0 bg-black/40"
        onClick={closeNotifications}
        aria-hidden="true"
      />

      <div
        className="absolute top-0 right-0 w-full max-h-[70dvh] rounded-b-2xl overflow-hidden
          dark:bg-untold-surface light:bg-white shadow-2xl animate-slide-up
          pt-[env(safe-area-inset-top)]"
      >
        <div className="flex items-center justify-between px-4 py-3 border-b dark:border-untold-border light:border-gray-100">
          <div>
            <h2 className="text-base font-semibold dark:text-untold-white light:text-black">
              Notifications
            </h2>
            {unread > 0 && (
              <p className="text-xs text-untold-gold">{unread} unread</p>
            )}
          </div>
          <button
            onClick={closeNotifications}
            className="p-2 rounded-full dark:hover:bg-white/10 light:hover:bg-black/5"
            aria-label="Close notifications"
          >
            <CloseIcon className="w-5 h-5" />
          </button>
        </div>

        <div className="overflow-y-auto max-h-[calc(70dvh-56px)]">
          {notifications.map((n) => (
            <div
              key={n.id}
              className={`px-4 py-3.5 border-b dark:border-untold-border/50 light:border-gray-50
                ${!n.read ? 'dark:bg-untold-gold/5 light:bg-untold-gold/10' : ''}`}
            >
              <div className="flex items-start gap-3">
                {!n.read && (
                  <span className="mt-1.5 w-2 h-2 rounded-full bg-untold-gold shrink-0" />
                )}
                <div className={!n.read ? '' : 'ml-5'}>
                  <p className="text-sm font-medium dark:text-untold-white light:text-black">
                    {n.title}
                  </p>
                  <p className="text-xs dark:text-untold-muted light:text-gray-500 mt-0.5 leading-relaxed">
                    {n.message}
                  </p>
                  <p className="text-[10px] dark:text-untold-muted/70 light:text-gray-400 mt-1">
                    {n.time}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
