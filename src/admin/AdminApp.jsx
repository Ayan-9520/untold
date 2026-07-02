import { Suspense } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { studioPath } from '../config/ecosystem';
import { AdminAuthProvider } from './context/AdminAuthContext';
import QueryProvider from './providers/QueryProvider';
import ProtectedRoute from './components/ProtectedRoute';
import AdminLayout from './layout/AdminLayout';
import StudioErrorBoundary from './components/StudioErrorBoundary';
import Loader from '../components/ui/Loader';
import LoginPage from './pages/LoginPage';
import * as Pages from './routes/lazyPages';

function StudioRoute({ children }) {
  return (
    <StudioErrorBoundary>
      <Suspense fallback={<Loader fullScreen />}>{children}</Suspense>
    </StudioErrorBoundary>
  );
}

export default function AdminApp() {
  return (
    <AdminAuthProvider>
      <QueryProvider>
        <Routes>
          <Route path="login" element={<LoginPage />} />
          <Route
            element={
              <ProtectedRoute>
                <AdminLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<StudioRoute><Pages.DashboardPage /></StudioRoute>} />
            <Route path="dashboard" element={<StudioRoute><Pages.DashboardPage /></StudioRoute>} />
            <Route path="projects" element={<StudioRoute><Pages.ProjectsPage /></StudioRoute>} />
            <Route path="projects/:id" element={<StudioRoute><Pages.ProjectDetailPage /></StudioRoute>} />
            <Route path="research" element={<StudioRoute><Pages.ResearchPage /></StudioRoute>} />
            <Route path="research/:projectId" element={<StudioRoute><Pages.ResearchWorkspacePage /></StudioRoute>} />
            <Route path="pipeline" element={<StudioRoute><Pages.ProductionPipelinePage /></StudioRoute>} />
            <Route path="workflows" element={<StudioRoute><Pages.WorkflowDashboardPage /></StudioRoute>} />
            <Route path="workflows/builder/:definitionId" element={<StudioRoute><Pages.WorkflowBuilderPage /></StudioRoute>} />
            <Route path="workflows/runs/:runId" element={<StudioRoute><Pages.WorkflowRunPage /></StudioRoute>} />
            <Route path="bi" element={<StudioRoute><Pages.BusinessIntelligencePage /></StudioRoute>} />
            <Route path="marketplace" element={<StudioRoute><Pages.AgentMarketplacePage /></StudioRoute>} />
            <Route path="plugins" element={<StudioRoute><Pages.PluginMarketplacePage /></StudioRoute>} />
            <Route path="plugins/docs" element={<StudioRoute><Pages.PluginDocsPage /></StudioRoute>} />
            <Route path="api-gateway" element={<StudioRoute><Pages.ApiGatewayPage /></StudioRoute>} />
            <Route path="security" element={<StudioRoute><Pages.SecurityDashboardPage /></StudioRoute>} />
            <Route path="compliance" element={<StudioRoute><Pages.CompliancePage /></StudioRoute>} />
            <Route path="ai-cost" element={<StudioRoute><Pages.AICostOptimizationPage /></StudioRoute>} />
            <Route path="collaboration" element={<StudioRoute><Pages.CollaborationPage /></StudioRoute>} />
            <Route path="collaboration/:projectId" element={<StudioRoute><Pages.CollaborationPage /></StudioRoute>} />
            <Route path="scripts" element={<StudioRoute><Pages.ScriptsPage /></StudioRoute>} />
            <Route path="scripts/:projectId" element={<StudioRoute><Pages.ScriptWorkspacePage /></StudioRoute>} />
            <Route path="storyboard" element={<StudioRoute><Pages.StoryboardPage /></StudioRoute>} />
            <Route path="storyboard/:projectId" element={<StudioRoute><Pages.StoryboardWorkspacePage /></StudioRoute>} />
            <Route path="assets" element={<StudioRoute><Pages.AssetsPage /></StudioRoute>} />
            <Route path="timeline" element={<StudioRoute><Pages.TimelinePage /></StudioRoute>} />
            <Route path="timeline/:projectId" element={<StudioRoute><Pages.TimelineWorkspacePage /></StudioRoute>} />
            <Route path="content" element={<StudioRoute><Pages.ContentPage /></StudioRoute>} />
            <Route path="content/:projectId" element={<StudioRoute><Pages.PublishingWorkspacePage /></StudioRoute>} />
            <Route path="publishing" element={<StudioRoute><Pages.ContentPage /></StudioRoute>} />
            <Route path="publishing/:projectId" element={<StudioRoute><Pages.PublishingWorkspacePage /></StudioRoute>} />
            <Route path="ai" element={<StudioRoute><Pages.AICommandPage /></StudioRoute>} />
            <Route path="images" element={<StudioRoute><Pages.ImageStudioPage /></StudioRoute>} />
            <Route path="videos" element={<StudioRoute><Pages.VideoStudioPage /></StudioRoute>} />
            <Route path="voice" element={<StudioRoute><Pages.VoiceStudioPage /></StudioRoute>} />
            <Route path="music" element={<StudioRoute><Pages.MusicStudioPage /></StudioRoute>} />
            <Route path="shorts" element={<StudioRoute><Pages.ShortsStudioPage /></StudioRoute>} />
            <Route path="seo" element={<StudioRoute><Pages.SEOStudioPage /></StudioRoute>} />
            <Route path="translation" element={<StudioRoute><Pages.TranslationStudioPage /></StudioRoute>} />
            <Route path="publishing-agent" element={<StudioRoute><Pages.PublishingAgentPage /></StudioRoute>} />
            <Route path="team" element={<StudioRoute><Pages.StudioPage /></StudioRoute>} />
            <Route path="ecosystem" element={<StudioRoute><Pages.EcosystemPage /></StudioRoute>} />
            <Route path="ai-localization" element={<StudioRoute><Pages.AILocalizationPage /></StudioRoute>} />
            <Route path="magazine" element={<StudioRoute><Pages.MagazinePage /></StudioRoute>} />
            <Route path="users" element={<StudioRoute><Pages.UsersPage /></StudioRoute>} />
            <Route path="admin" element={<StudioRoute><Pages.AdminPanelPage /></StudioRoute>} />
            <Route path="settings" element={<StudioRoute><Pages.AdminPanelPage /></StudioRoute>} />
            <Route path="membership" element={<StudioRoute><Pages.MembershipPage /></StudioRoute>} />
            <Route path="analytics" element={<StudioRoute><Pages.AnalyticsPage /></StudioRoute>} />
            <Route path="revenue" element={<StudioRoute><Pages.RevenuePage /></StudioRoute>} />
            <Route path="notifications" element={<StudioRoute><Pages.NotificationsPage /></StudioRoute>} />
          </Route>
          <Route path="*" element={<Navigate to={studioPath()} replace />} />
        </Routes>
      </QueryProvider>
    </AdminAuthProvider>
  );
}
