import { createContext, useContext, useState, useCallback } from 'react';

const AppUIContext = createContext(null);

export function AppUIProvider({ children }) {
  const [searchOpen, setSearchOpen] = useState(false);
  const [notificationsOpen, setNotificationsOpen] = useState(false);

  const openSearch = useCallback(() => {
    setNotificationsOpen(false);
    setSearchOpen(true);
  }, []);

  const closeSearch = useCallback(() => setSearchOpen(false), []);

  const openNotifications = useCallback(() => {
    setSearchOpen(false);
    setNotificationsOpen(true);
  }, []);

  const closeNotifications = useCallback(() => setNotificationsOpen(false), []);

  return (
    <AppUIContext.Provider
      value={{
        searchOpen,
        notificationsOpen,
        openSearch,
        closeSearch,
        openNotifications,
        closeNotifications,
      }}
    >
      {children}
    </AppUIContext.Provider>
  );
}

export function useAppUI() {
  const ctx = useContext(AppUIContext);
  if (!ctx) throw new Error('useAppUI must be used within AppUIProvider');
  return ctx;
}
