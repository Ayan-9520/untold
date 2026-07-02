import { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import SEO from '../components/SEO';
import { useWebAuth } from '../context/WebAuthContext';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useWebAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from?.pathname || '/';

  const inputClass = `w-full rounded-xl px-4 py-3 text-sm outline-none border
    dark:bg-untold-surface dark:border-untold-border dark:text-untold-white
    light:bg-gray-50 light:border-gray-200 light:text-black focus:ring-2 focus:ring-untold-gold`;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      await login({ email, password });
      navigate(from, { replace: true });
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed. Check credentials or start the backend.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <SEO title="Login" description="Sign in to UNTOLD" path="/login" />
      <section className="pt-28 pb-16 min-h-[70vh] flex items-center">
        <div className="mx-auto w-full max-w-md px-4">
          <h1 className="font-display text-3xl font-bold dark:text-untold-white light:text-black">Welcome back</h1>
          <p className="mt-2 text-sm dark:text-untold-muted light:text-gray-500">The Story Behind The Glory</p>
          <form onSubmit={handleSubmit} className="mt-8 space-y-4">
            <input type="email" required placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} className={inputClass} />
            <input type="password" required placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} className={inputClass} />
            <p className="text-right text-sm">
              <Link to="/forgot-password" className="text-untold-gold font-medium">Forgot password?</Link>
            </p>
            {error && <p className="text-sm text-red-400">{error}</p>}
            <button type="submit" disabled={loading} className="w-full py-3 rounded-xl bg-untold-gold text-untold-dark font-semibold disabled:opacity-60">
              {loading ? 'Signing in…' : 'Sign In'}
            </button>
          </form>
          <p className="mt-6 text-center text-sm dark:text-untold-muted light:text-gray-500">
            No account? <Link to="/signup" className="text-untold-gold font-medium">Create one</Link>
          </p>
        </div>
      </section>
    </>
  );
}
