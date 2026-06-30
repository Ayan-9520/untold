import type { StudioRole } from '@/features/auth/types';

/** Nav items visible per role (admin sees all). */
const ROLE_NAV: Record<string, StudioRole[]> = {
  'studio.access': ['admin', 'producer', 'researcher', 'writer', 'editor', 'designer', 'publisher', 'viewer'],
  'team.manage': ['admin', 'producer'],
  'settings.manage': ['admin'],
};

export function canAccess(permission: string, role: StudioRole, permissions?: string[]): boolean {
  if (role === 'admin') return true;
  if (permissions?.includes(permission)) return true;
  const allowed = ROLE_NAV[permission];
  return allowed ? allowed.includes(role) : true;
}

export function hasRole(userRole: StudioRole, allowed: StudioRole[]): boolean {
  if (userRole === 'admin') return true;
  return allowed.includes(userRole);
}
