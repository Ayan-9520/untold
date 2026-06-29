import { Outlet, useLocation } from 'react-router-dom';
import BottomNav from './BottomNav';
import AppSiteNav from './AppSiteNav';
import SearchOverlay from '../components/SearchOverlay';
import NotificationPanel from '../components/NotificationPanel';

const HIDE_SHELL_NAV = ['/app', '/app/login', '/app/signup', '/app/auth'];
const HIDE_TOP_NAV = ['/app/shorts'];
const HIDE_BOTTOM_NAV = [...HIDE_SHELL_NAV, '/app/watch'];

export default function AppShell() {
  const { pathname } = useLocation();
  const isWatch = pathname.startsWith('/app/watch/');
  const showBottom = !HIDE_BOTTOM_NAV.some((p) => pathname === p) && !isWatch;
  const showTop = !HIDE_TOP_NAV.includes(pathname) && !isWatch;

  return (
    <div className="app-shell relative min-h-dvh dark:bg-untold-dark light:bg-gray-100">
      <div className="mx-auto w-full max-w-[430px] min-h-dvh relative flex flex-col shadow-2xl dark:shadow-black/50 dark:bg-untold-dark light:bg-white">
        {showTop && <AppSiteNav />}
        <main className="flex-1 min-h-0 w-full">
          <Outlet />
        </main>
        {showBottom && <BottomNav />}
        <SearchOverlay />
        <NotificationPanel />
      </div>
    </div>
  );
}
