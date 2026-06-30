import { NavLink } from 'react-router-dom';
import { MAIN_NAV, PRODUCTION_NAV, OPS_NAV, type NavItem } from '@/config/navigation';
import { useAuth } from '@/features/auth/AuthProvider';
import { cn } from '@/lib/utils';

function NavSection({ title, items }: { title: string; items: NavItem[] }) {
  const { hasRole } = useAuth();
  const visible = items.filter((item) => !item.roles || hasRole(item.roles));
  if (!visible.length) return null;

  return (
    <div className="mb-5">
      <p className="px-3 mb-2 text-[10px] font-semibold uppercase tracking-wider text-studio-muted/70">{title}</p>
      <div className="space-y-0.5">
        {visible.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) => cn('studio-sidebar-link', isActive && 'studio-sidebar-link--active')}
          >
            <Icon className="w-4 h-4 shrink-0" />
            <span className="truncate">{label}</span>
          </NavLink>
        ))}
      </div>
    </div>
  );
}

export default function Sidebar() {
  return (
    <aside className="hidden lg:flex w-64 shrink-0 flex-col border-r border-studio-border bg-studio-surface/90 backdrop-blur-md">
      <div className="p-5 border-b border-studio-border">
        <p className="text-[10px] font-bold tracking-[0.35em] text-studio-gold uppercase">UNTOLD</p>
        <p className="text-xl font-bold text-white mt-1">Studio</p>
        <p className="text-[10px] text-studio-muted mt-1">Production OS</p>
      </div>
      <nav className="flex-1 overflow-y-auto p-3">
        <NavSection title="Core" items={MAIN_NAV} />
        <NavSection title="Production" items={PRODUCTION_NAV} />
        <NavSection title="Operations" items={OPS_NAV} />
      </nav>
    </aside>
  );
}
