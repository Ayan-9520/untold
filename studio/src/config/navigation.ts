import type { LucideIcon } from 'lucide-react';
import {
  LayoutDashboard, Film, Search, FileText, Scissors, Image, Video, Mic, Music,
  Upload, BarChart3, Bell, Users, Calendar, CheckSquare, Settings, Sparkles,
} from 'lucide-react';
import type { StudioRole } from '@/features/auth/types';

export interface NavItem {
  to: string;
  label: string;
  icon: LucideIcon;
  end?: boolean;
  roles?: StudioRole[];
}

export const MAIN_NAV: NavItem[] = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard, end: true },
  { to: '/projects', label: 'Projects', icon: Film },
  { to: '/research', label: 'Research Desk', icon: Search, roles: ['admin', 'producer', 'researcher'] },
  { to: '/scripts', label: 'Script Writer', icon: FileText, roles: ['admin', 'producer', 'writer'] },
  { to: '/storyboard', label: 'Storyboard', icon: Scissors, roles: ['admin', 'producer', 'editor', 'designer'] },
  { to: '/assets', label: 'Asset Library', icon: Image },
];

export const PRODUCTION_NAV: NavItem[] = [
  { to: '/ai-image', label: 'AI Image', icon: Sparkles },
  { to: '/ai-video', label: 'AI Video', icon: Video },
  { to: '/voice', label: 'Voice Studio', icon: Mic },
  { to: '/music', label: 'Music Library', icon: Music },
  { to: '/editor', label: 'Timeline Editor', icon: Scissors, roles: ['admin', 'producer', 'editor'] },
  { to: '/publish', label: 'Publishing CMS', icon: Upload, roles: ['admin', 'producer', 'publisher'] },
];

export const OPS_NAV: NavItem[] = [
  { to: '/analytics', label: 'Analytics', icon: BarChart3 },
  { to: '/notifications', label: 'Notifications', icon: Bell },
  { to: '/team', label: 'Team', icon: Users, roles: ['admin', 'producer'] },
  { to: '/calendar', label: 'Calendar', icon: Calendar },
  { to: '/tasks', label: 'Tasks', icon: CheckSquare },
  { to: '/approvals', label: 'Approvals', icon: CheckSquare },
  { to: '/settings', label: 'Settings', icon: Settings, roles: ['admin'] },
];
