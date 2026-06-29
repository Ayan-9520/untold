import { useState } from 'react';
import { useNavigate, Navigate } from 'react-router-dom';
import { useAdminAuth } from '../context/AdminAuthContext';
import { useTheme } from '../../context/ThemeContext';
import { SunIcon, MoonIcon } from '../../components/icons';
import Logo from '../../components/brand/Logo';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login, isAuthenticated, isAdmin, loading: authLoading } = useAdminAuth();
  const { isDark, toggleTheme } = useTheme();
  const navigate = useNavigate();

  if (!authLoading && isAuthenticated && isAdmin) {
    return <Navigate to="/admin" replace />;
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      await login(email, password);
      navigate('/admin');
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(typeof detail === 'string' ? detail : Array.isArray(detail) ? detail[0]?.msg : err.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const inputClass = `w-full rounded-lg px-4 py-3 text-sm outline-none border
    dark:bg-untold-dark dark:border-white/10 dark:text-untold-white
    light:bg-white light:border-gray-200 light:text-black
    focus:ring-2 focus:ring-untold-gold/40`;

  return (
    <div className="min-h-screen flex dark:bg-untold-dark light:bg-gray-100">
      <div className="hidden lg:flex flex-1 relative overflow-hidden items-center justify-center p-12">
        <div className="absolute inset-0 bg-gradient-to-br from-untold-gold/20 via-transparent to-untold-dark" />
        <div className="relative text-center flex flex-col items-center">
          <Logo variant="full" className="mx-auto !max-w-[260px]" />
          <p className="mt-6 text-lg dark:text-untold-muted light:text-gray-500">Admin Console</p>
        </div>
      </div>

      <div className="flex-1 flex flex-col justify-center px-6 sm:px-12 lg:px-16 py-12">
        <div className="flex justify-end mb-8">
          <button onClick={toggleTheme} className="p-2 rounded-lg hover:dark:bg-white/10 hover:light:bg-black/5">
            {isDark ? <SunIcon className="w-5 h-5 text-untold-gold" /> : <MoonIcon className="w-5 h-5 text-untold-gold" />}
          </button>
        </div>

        <div className="max-w-md w-full mx-auto">
          <h2 className="text-2xl font-bold dark:text-untold-white light:text-black">Welcome back</h2>
          <p className="mt-1 text-sm dark:text-untold-muted light:text-gray-500">
            Sign in with your admin credentials
          </p>

          <form onSubmit={handleSubmit} className="mt-8 space-y-4">
            <div>
              <label className="block text-xs font-medium dark:text-untold-muted light:text-gray-500 mb-1.5">
                Email
              </label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className={inputClass}
                placeholder="admin@untold.com"
              />
            </div>
            <div>
              <label className="block text-xs font-medium dark:text-untold-muted light:text-gray-500 mb-1.5">
                Password
              </label>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className={inputClass}
                placeholder="••••••••"
              />
            </div>

            {error && (
              <p className="text-sm text-red-400 bg-red-500/10 px-3 py-2 rounded-lg">{error}</p>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 rounded-lg bg-untold-gold text-untold-dark font-semibold text-sm
                hover:bg-untold-gold-light transition-colors disabled:opacity-60"
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
