import { Navigate } from 'react-router-dom';
import { useAuth } from '@/features/auth/AuthProvider';
import type { StudioRole } from '@/features/auth/types';

export default function RoleRoute({ roles, children }: { roles: StudioRole[]; children: React.ReactNode }) {
  const { hasRole } = useAuth();

  if (!hasRole(roles)) {
    return <Navigate to="/" replace />;
  }

  return children;
}
