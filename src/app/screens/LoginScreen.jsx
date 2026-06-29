import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AppAuthContext';
import { useTheme } from '../../context/ThemeContext';
import Logo from '../../components/brand/Logo';
import { SunIcon, MoonIcon } from '../../components/icons';

export default function LoginScreen() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const { isDark, toggleTheme } = useTheme();
  const navigate = useNavigate();

  const inputClass = `w-full rounded-xl px-4 py-3.5 text-sm outline-none border
    dark:bg-untold-surface dark:border-untold-border dark:text-untold-white
    light:bg-gray-50 light:border-gray-200 light:text-black
    focus:ring-2 focus:ring-untold-gold/50`;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      await login({ email, password });
      navigate('/app/home', { replace: true });
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-dvh dark:bg-untold-dark light:bg-white flex flex-col px-6 pt-[env(safe-area-inset-top)]">
      <div className="flex justify-between items-center py-4">
        <Logo variant="nav" />
        <button onClick={toggleTheme} className="p-2 rounded-full dark:hover:bg-white/10">
          {isDark ? <SunIcon className="w-5 h-5 text-untold-gold" /> : <MoonIcon className="w-5 h-5 text-untold-gold" />}
        </button>
      </div>

      <div className="flex-1 flex flex-col justify-center pb-12 max-w-md mx-auto w-full animate-slide-up">
        <h1 className="text-2xl font-bold dark:text-untold-white light:text-black">Welcome back</h1>
        <p className="text-sm dark:text-untold-muted light:text-gray-500 mt-1">Sign in to continue watching</p>

        <form onSubmit={handleSubmit} className="mt-8 space-y-4">
          <input type="email" required placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} className={inputClass} />
          <input type="password" required placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} className={inputClass} />
          {error && <p className="text-sm text-red-400">{error}</p>}
          <button type="submit" disabled={loading} className="w-full py-3.5 rounded-xl bg-untold-gold text-untold-dark font-semibold disabled:opacity-60">
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <p className="mt-6 text-center text-sm dark:text-untold-muted light:text-gray-500">
          No account?{' '}
          <Link to="/app/signup" className="text-untold-gold font-medium">Create one</Link>
        </p>
        <button onClick={() => navigate('/app/home')} className="mt-4 text-sm text-center dark:text-untold-muted light:text-gray-400 w-full">
          Continue as guest
        </button>
      </div>
    </div>
  );
}
