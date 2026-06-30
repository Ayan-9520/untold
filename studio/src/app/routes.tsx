import { Routes, Route, Navigate } from 'react-router-dom';
import ProtectedRoute from '@/components/routing/ProtectedRoute';
import AppShell from '@/components/layout/AppShell';
import LoginPage from '@/features/auth/LoginPage';
import DashboardPage from '@/pages/DashboardPage';
import ProjectsPage from '@/pages/ProjectsPage';
import ModulePage from '@/components/ModulePage';
import RoleRoute from '@/components/routing/RoleRoute';

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route element={<ProtectedRoute />}>
        <Route element={<AppShell />}>
          <Route index element={<DashboardPage />} />
          <Route path="projects" element={<ProjectsPage />} />
          <Route path="research" element={<RoleRoute roles={['admin', 'producer', 'researcher']}><ModulePage title="Research Desk" description="Topic input, AI research, sources, fact collection, approval workflow." /></RoleRoute>} />
          <Route path="scripts" element={<RoleRoute roles={['admin', 'producer', 'writer']}><ModulePage title="Script Writer" description="Rich text editor, version history, AI generator, collaboration." /></RoleRoute>} />
          <Route path="storyboard" element={<ModulePage title="Storyboard" description="Scene generation from scripts." />} />
          <Route path="assets" element={<ModulePage title="Asset Library" description="Cloudflare R2 media storage." />} />
          <Route path="ai-image" element={<ModulePage title="AI Image Studio" description="Landscape, portrait, thumbnail, poster generation." />} />
          <Route path="ai-video" element={<ModulePage title="AI Video Studio" description="B-roll, animation, Celery queued jobs." />} />
          <Route path="voice" element={<ModulePage title="Voice Studio" description="Multi-language narration." />} />
          <Route path="music" element={<ModulePage title="Music Library" description="Licensed tracks and SFX." />} />
          <Route path="editor" element={<ModulePage title="Timeline Editor" description="Trim, split, captions, export." />} />
          <Route path="publish" element={<RoleRoute roles={['admin', 'producer', 'publisher']}><ModulePage title="Publishing CMS" description="Publish to Originals and social platforms." /></RoleRoute>} />
          <Route path="analytics" element={<ModulePage title="Analytics" description="Views, CTR, watch time, revenue." />} />
          <Route path="notifications" element={<ModulePage title="Notifications" description="Realtime WebSocket alerts." />} />
          <Route path="team" element={<RoleRoute roles={['admin', 'producer']}><ModulePage title="Team Management" description="RBAC roles and permissions." /></RoleRoute>} />
          <Route path="calendar" element={<ModulePage title="Calendar" description="Production schedule." />} />
          <Route path="tasks" element={<ModulePage title="Tasks" description="Assign and track production tasks." />} />
          <Route path="approvals" element={<ModulePage title="Approvals" description="Research, script, publish approvals." />} />
          <Route path="settings" element={<RoleRoute roles={['admin']}><ModulePage title="Settings" description="Studio configuration." /></RoleRoute>} />
        </Route>
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
