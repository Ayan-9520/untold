import { Link } from 'react-router-dom';
import { Bell, LogOut, Menu, Moon, Search, Sun } from 'lucide-react';
import { useAuth } from '@/features/auth/AuthProvider';
import { useTheme } from '@/providers/ThemeProvider';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

interface TopbarProps {
  onMenuClick?: () => void;
}

export default function Topbar({ onMenuClick }: TopbarProps) {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();

  return (
    <header className="sticky top-0 z-30 flex h-14 items-center gap-4 border-b border-studio-border bg-studio-black/80 backdrop-blur-md px-4 lg:px-6">
      <button
        type="button"
        className="lg:hidden p-2 rounded-lg text-studio-muted hover:text-white hover:bg-white/5"
        onClick={onMenuClick}
        aria-label="Open menu"
      >
        <Menu className="w-5 h-5" />
      </button>

      <div className="hidden sm:flex flex-1 max-w-md items-center gap-2 rounded-lg border border-studio-border bg-studio-surface/60 px-3 py-2">
        <Search className="w-4 h-4 text-studio-muted shrink-0" />
        <input
          type="search"
          placeholder="Search projects, scripts, assets…"
          className="w-full bg-transparent text-sm text-white placeholder:text-studio-muted focus:outline-none"
        />
      </div>

      <div className="flex-1 lg:flex-none" />

      <Link
        to="/notifications"
        className="inline-flex h-9 w-9 items-center justify-center rounded-lg text-studio-muted hover:text-white hover:bg-white/5"
        aria-label="Notifications"
      >
        <Bell className="w-4 h-4" />
      </Link>

      <Button variant="ghost" size="icon" onClick={toggleTheme} aria-label="Toggle theme">
        {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
      </Button>

      {user && (
        <div className="flex items-center gap-3 pl-2 border-l border-studio-border">
          <div className="hidden md:block text-right">
            <p className="text-xs font-medium text-white leading-tight">{user.full_name}</p>
            <Badge variant="gold" className="mt-0.5 capitalize">{user.studio_role}</Badge>
          </div>
          <Button variant="ghost" size="icon" onClick={logout} aria-label="Sign out">
            <LogOut className="w-4 h-4" />
          </Button>
        </div>
      )}
    </header>
  );
}
