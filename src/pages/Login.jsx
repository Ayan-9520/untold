import { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import SEO from '../components/SEO';
import { useWebAuth } from '../context/WebAuthContext';

export default function Login() {
  const { t } = useTranslation();
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
      setError(err.response?.data?.detail || t('auth.loginFailed'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <SEO title={t('auth.signIn')} description={t('brand.tagline')} path="/login" />
      <section className="pt-28 pb-16 min-h-[70vh] flex items-center">
        <div className="mx-auto w-full max-w-md px-4">
          <h1 className="font-display text-3xl font-bold dark:text-untold-white light:text-black">{t('auth.welcomeBack')}</h1>
          <p className="mt-2 text-sm dark:text-untold-muted light:text-gray-500">{t('brand.tagline')}</p>
          <form onSubmit={handleSubmit} className="mt-8 space-y-4">
            <input type="email" required placeholder={t('auth.email')} value={email} onChange={(e) => setEmail(e.target.value)} className={inputClass} />
            <input type="password" required placeholder={t('auth.password')} value={password} onChange={(e) => setPassword(e.target.value)} className={inputClass} />
            <p className="text-right text-sm">
              <Link to="/forgot-password" className="text-untold-gold font-medium">{t('auth.forgotPassword')}</Link>
            </p>
            {error && <p className="text-sm text-red-400">{error}</p>}
            <button type="submit" disabled={loading} className="w-full py-3 rounded-xl bg-untold-gold text-untold-dark font-semibold disabled:opacity-60">
              {loading ? t('auth.signingIn') : t('auth.signIn')}
            </button>
          </form>
          <p className="mt-6 text-center text-sm dark:text-untold-muted light:text-gray-500">
            {t('auth.noAccount')}{' '}
            <Link to="/signup" className="text-untold-gold font-medium">{t('auth.signUp')}</Link>
          </p>
        </div>
      </section>
    </>
  );
}
