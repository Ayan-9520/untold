import { Navigate } from 'react-router-dom';
import { useAdminAuth } from '../context/AdminAuthContext';
import { PRODUCTS } from '../../config/ecosystem';

export default function ProtectedRoute({ children }) {
  const { isAuthenticated, hasStudioAccess, loading } = useAdminAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center dark:bg-untold-dark light:bg-gray-50">
        <div className="w-10 h-10 border-2 border-untold-gold border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!isAuthenticated || !hasStudioAccess) {
    return <Navigate to={PRODUCTS.STUDIO.loginPath} replace />;
  }

  return children;
}
