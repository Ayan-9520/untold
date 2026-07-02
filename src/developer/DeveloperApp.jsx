import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { NavLink, Outlet, Routes, Route, Navigate } from 'react-router-dom';
import HomePage from './pages/HomePage';
import DocsPage from './pages/DocsPage';
import KeysPage from './pages/KeysPage';
import WebhooksPage from './pages/WebhooksPage';
import UsagePage from './pages/UsagePage';

const nav = [
  { to: '/developers', end: true, label: 'Overview' },
  { to: '/developers/docs', label: 'Documentation' },
  { to: '/developers/keys', label: 'API Keys' },
  { to: '/developers/webhooks', label: 'Webhooks' },
  { to: '/developers/usage', label: 'Usage' },
];

const devQueryClient = new QueryClient({ defaultOptions: { queries: { staleTime: 30_000 } } });

function RequireAuth({ children }) {
  const token = localStorage.getItem('untold-token');
  if (!token) {
    return <Navigate to="/login" state={{ from: { pathname: window.location.pathname } }} replace />;
  }
  return children;
}

function Layout() {
  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white">
      <header className="border-b border-neutral-800">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
          <div>
            <div className="text-xs uppercase tracking-widest text-rose-500">UNTOLD</div>
            <h1 className="text-lg font-semibold">Developer Platform</h1>
          </div>
          <nav className="flex gap-4 text-sm">
            {nav.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.end}
                className={({ isActive }) =>
                  isActive ? 'text-rose-400' : 'text-neutral-400 hover:text-white'
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-4 py-8">
        <Outlet />
      </main>
    </div>
  );
}

export default function DeveloperApp() {
  return (
    <QueryClientProvider client={devQueryClient}>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<HomePage />} />
          <Route path="docs" element={<DocsPage />} />
          <Route
            path="keys"
            element={
              <RequireAuth>
                <KeysPage />
              </RequireAuth>
            }
          />
          <Route
            path="webhooks"
            element={
              <RequireAuth>
                <WebhooksPage />
              </RequireAuth>
            }
          />
          <Route
            path="usage"
            element={
              <RequireAuth>
                <UsagePage />
              </RequireAuth>
            }
          />
          <Route path="*" element={<Navigate to="/developers" replace />} />
        </Route>
      </Routes>
    </QueryClientProvider>
  );
}
