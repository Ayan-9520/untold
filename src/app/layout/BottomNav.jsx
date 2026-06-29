import { NavLink } from 'react-router-dom';
import { HomeIcon, FilmIcon, ShortsIcon, BookmarkIcon, UserIcon } from '../../components/icons';

const tabs = [
  { to: '/app/home', icon: HomeIcon, label: 'Home' },
  { to: '/app/originals', icon: FilmIcon, label: 'Originals' },
  { to: '/app/shorts', icon: ShortsIcon, label: 'Shorts' },
  { to: '/app/watchlist', icon: BookmarkIcon, label: 'List' },
  { to: '/app/profile', icon: UserIcon, label: 'Profile' },
];

export default function BottomNav() {
  return (
    <nav
      className="sticky bottom-0 z-40 w-full
        dark:bg-untold-dark/98 light:bg-white/98 backdrop-blur-xl
        border-t dark:border-untold-border/60 light:border-gray-200/80
        pb-[max(0.5rem,env(safe-area-inset-bottom))]"
      aria-label="Main navigation"
    >
      <div className="flex items-stretch justify-around min-h-[3.5rem] px-1 sm:px-2">
        {tabs.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex flex-1 flex-col items-center justify-center gap-0.5 py-1.5 min-w-0 max-w-[5.5rem] transition-colors
              ${isActive ? 'text-untold-gold' : 'dark:text-untold-muted light:text-gray-500'}`
            }
          >
            {({ isActive }) => (
              <>
                <Icon className={`w-5 h-5 sm:w-[1.35rem] sm:h-[1.35rem] shrink-0 ${isActive ? 'scale-110' : ''} transition-transform`} />
                <span className="text-[9px] sm:text-[10px] font-semibold tracking-wide truncate w-full text-center leading-tight">
                  {label}
                </span>
              </>
            )}
          </NavLink>
        ))}
      </div>
    </nav>
  );
}
