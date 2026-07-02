import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from './context/ThemeContext';
import { WatchlistProvider } from './context/WatchlistContext';
import { EngagementProvider } from './context/EngagementContext';
import { LocaleProvider } from './context/LocaleContext';
import { WebAuthProvider } from './context/WebAuthContext';
import { ViewerProfileProvider } from './context/ViewerProfileContext';
import ProfilePickerGate from './components/profile/ProfilePickerGate';
import Navbar from './components/layout/Navbar';
import Footer from './components/layout/Footer';
import WebRoutes from './routes/WebRoutes';
import MobileApp from './app/MobileApp';
import AdminApp from './admin/AdminApp';
import AIApp from './ai/AIApp';
import AdminLegacyRedirect from './routes/AdminLegacyRedirect';
import DeveloperApp from './developer/DeveloperApp';
import CookieConsent from './components/CookieConsent';

export default function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/app/*" element={<MobileApp />} />
          {/* UNTOLD STUDIO — internal production OS (team only) */}
          <Route path="/studio/*" element={<AdminApp />} />
          {/* Legacy /admin URLs → /studio */}
          <Route path="/admin/*" element={<AdminLegacyRedirect />} />
          {/* UNTOLD AI — Phase 2 SaaS (separate product) */}
          <Route path="/ai/*" element={<AIApp />} />
          {/* Public developer platform */}
          <Route path="/developers/*" element={<DeveloperApp />} />
          <Route
            path="/*"
            element={
              <WebAuthProvider>
              <ViewerProfileProvider>
              <WatchlistProvider>
                <LocaleProvider>
                <EngagementProvider>
                <ProfilePickerGate />
                <div className="flex min-h-screen flex-col">
                  <Navbar />
                  <main className="flex-1 pt-[calc(var(--nav-height-mobile)+var(--lang-bar-height))] md:pt-[calc(var(--nav-height)+var(--lang-bar-height))]">
                    <WebRoutes />
                  </main>
                  <Footer />
                  <CookieConsent />
                </div>
                </EngagementProvider>
                </LocaleProvider>
              </WatchlistProvider>
              </ViewerProfileProvider>
              </WebAuthProvider>
            }
          />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
}
