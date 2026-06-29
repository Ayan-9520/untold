import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AppAuthContext';
import { useTheme } from '../../context/ThemeContext';
import { SunIcon, MoonIcon } from '../../components/icons';

export default function AuthScreen() {
  const [mode, setMode] = useState('login');
  const [form, setForm] = useState({ name: '', email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login, register } = useAuth();
  const { isDark, toggleTheme } = useTheme();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      if (mode === 'login') {
        await login({ email: form.email, password: form.password });
      } else {
        await register(form);
      }
      navigate('/app/home', { replace: true });
    } catch (err) {
      setError(err.message || 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  const inputClass = `w-full rounded-xl px-4 py-3.5 text-sm outline-none transition-colors
    dark:bg-untold-surface dark:text-untold-white dark:border-untold-border
    light:bg-gray-50 light:text-black light:border-gray-200
    border focus:ring-2 focus:ring-untold-gold/50 focus:border-untold-gold`;

  return (
    <div className="min-h-dvh dark:bg-untold-dark light:bg-white flex flex-col px-6 pt-[env(safe-area-inset-top)]">
      <div className="flex justify-end py-4">
        <button
          onClick={toggleTheme}
          className="p-2 rounded-full dark:hover:bg-white/10 light:hover:bg-black/5"
          aria-label="Toggle theme"
        >
          {isDark ? (
            <SunIcon className="w-5 h-5 text-untold-gold" />
          ) : (
            <MoonIcon className="w-5 h-5 text-untold-gold" />
          )}
        </button>
      </div>

      <div className="flex-1 flex flex-col justify-center pb-12 animate-slide-up">
        <div className="text-center mb-10">
          <h1 className="font-display text-4xl font-bold text-gold-gradient tracking-widest">
            UNTOLD
          </h1>
          <p className="text-sm dark:text-untold-muted light:text-gray-500 mt-2">
            The Story Behind The Glory
          </p>
        </div>

        <div className="flex rounded-xl p-1 dark:bg-untold-surface light:bg-gray-100 mb-8">
          {['login', 'register'].map((m) => (
            <button
              key={m}
              onClick={() => { setMode(m); setError(''); }}
              className={`flex-1 py-2.5 rounded-lg text-sm font-medium capitalize transition-all duration-200
                ${mode === m
                  ? 'bg-untold-gold text-untold-dark shadow-sm'
                  : 'dark:text-untold-muted light:text-gray-500'
                }`}
            >
              {m}
            </button>
          ))}
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {mode === 'register' && (
            <input
              name="name"
              type="text"
              required
              placeholder="Full name"
              value={form.name}
              onChange={handleChange}
              className={inputClass}
            />
          )}
          <input
            name="email"
            type="email"
            required
            placeholder="Email address"
            value={form.email}
            onChange={handleChange}
            className={inputClass}
            autoComplete="email"
          />
          <input
            name="password"
            type="password"
            required
            placeholder="Password"
            value={form.password}
            onChange={handleChange}
            className={inputClass}
            autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
          />

          {error && (
            <p className="text-sm text-red-500 text-center" role="alert">{error}</p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3.5 rounded-xl bg-untold-gold text-untold-dark font-semibold text-sm
              active:scale-[0.98] transition-transform disabled:opacity-60 mt-2"
          >
            {loading ? 'Please wait...' : mode === 'login' ? 'Sign In' : 'Create Account'}
          </button>
        </form>

        <button
          onClick={() => navigate('/app/home')}
          className="mt-6 text-sm text-center dark:text-untold-muted light:text-gray-500
            hover:text-untold-gold transition-colors"
        >
          Continue as guest
        </button>
      </div>
    </div>
  );
}
