import { Routes, Route, Navigate } from 'react-router-dom';
import AIHomePage from './pages/AIHomePage';

/** UNTOLD AI — Phase 2 SaaS (separate product, not linked from public OTT nav) */
export default function AIApp() {
  return (
    <Routes>
      <Route index element={<AIHomePage />} />
      <Route path="*" element={<Navigate to="/ai" replace />} />
    </Routes>
  );
}
