import { Navigate, useLocation } from 'react-router-dom';

/** Keeps old /admin bookmarks working — forwards to /studio */
export default function AdminLegacyRedirect() {
  const { pathname, search, hash } = useLocation();
  const next = pathname.replace(/^\/admin/, '/studio') + search + hash;
  return <Navigate to={next} replace />;
}
