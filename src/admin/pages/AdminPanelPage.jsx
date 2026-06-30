import StudioPageHeader from '../components/StudioPageHeader';
import StudioLiveBadge from '../components/StudioLiveBadge';
import AdminPanelDashboard from '../features/admin-panel/components/AdminPanelDashboard';
import { useAdminOverview } from '../features/admin-panel/hooks/useAdminPanel';

export default function AdminPanelPage() {
  const { isError } = useAdminOverview();

  return (
    <div className="space-y-6 animate-fade-in">
      <StudioPageHeader
        section="Operations"
        title="Admin Panel"
        description="RBAC, users, audit logs, AI usage, storage, billing, API keys, health, security & backups."
      >
        <StudioLiveBadge live={!isError} />
      </StudioPageHeader>
      <AdminPanelDashboard />
    </div>
  );
}
