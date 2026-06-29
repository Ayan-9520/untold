import { Routes, Route, Navigate } from 'react-router-dom';
import { studioPath } from '../config/ecosystem';
import { AdminAuthProvider } from './context/AdminAuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import AdminLayout from './layout/AdminLayout';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import UsersPage from './pages/UsersPage';
import ContentPage from './pages/ContentPage';
import AnalyticsPage from './pages/AnalyticsPage';
import RevenuePage from './pages/RevenuePage';
import AICommandPage from './pages/AICommandPage';
import StudioPage from './pages/StudioPage';
import EcosystemPage from './pages/EcosystemPage';
import ResearchPage from './pages/ResearchPage';
import ScriptsPage from './pages/ScriptsPage';
import AssetsPage from './pages/AssetsPage';
import AILocalizationPage from './pages/AILocalizationPage';
import MembershipPage from './pages/MembershipPage';
import MagazinePage from './pages/MagazinePage';
import NotificationsPage from './pages/NotificationsPage';

export default function AdminApp() {
  return (
    <AdminAuthProvider>
      <Routes>
        <Route path="login" element={<LoginPage />} />
        <Route
          element={
            <ProtectedRoute>
              <AdminLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<DashboardPage />} />
          <Route path="research" element={<ResearchPage />} />
          <Route path="scripts" element={<ScriptsPage />} />
          <Route path="assets" element={<AssetsPage />} />
          <Route path="content" element={<ContentPage />} />
          <Route path="ai" element={<AICommandPage />} />
          <Route path="team" element={<StudioPage />} />
          <Route path="ecosystem" element={<EcosystemPage />} />
          <Route path="ai-localization" element={<AILocalizationPage />} />
          <Route path="magazine" element={<MagazinePage />} />
          <Route path="users" element={<UsersPage />} />
          <Route path="membership" element={<MembershipPage />} />
          <Route path="analytics" element={<AnalyticsPage />} />
          <Route path="revenue" element={<RevenuePage />} />
          <Route path="notifications" element={<NotificationsPage />} />
        </Route>
        <Route path="*" element={<Navigate to={studioPath()} replace />} />
      </Routes>
    </AdminAuthProvider>
  );
}
