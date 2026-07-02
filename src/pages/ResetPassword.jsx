import { useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import SEO from '../components/SEO';
import { api } from '../api/client';

export default function ResetPassword() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token') || '';
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const inputClass = `w-full rounded-xl px-4 py-3 text-sm outline-none border
    dark:bg-untold-surface dark:border-untold-border dark:text-untold-white
    light:bg-gray-50 light:border-gray-200 light:text-black focus:ring-2 focus:ring-untold-gold`;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (password !== confirm) {
      setError('Passwords do not match.');
      return;
    }
    if (!token) {
      setError('Invalid or missing reset token.');
      return;
    }
    setLoading(true);
    setError('');
    setMessage('');
    try {
      const res = await api.auth.resetPassword({ token, new_password: password });
      setMessage(res.message || 'Password updated.');
      setTimeout(() => navigate('/login', { replace: true }), 2000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Unable to reset password.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <SEO title="Reset Password" description="Set a new UNTOLD password" path="/reset-password" />
      <section className="pt-28 pb-16 min-h-[70vh] flex items-center">
        <div className="mx-auto w-full max-w-md px-4">
          <h1 className="font-display text-3xl font-bold dark:text-untold-white light:text-black">Reset password</h1>
          <p className="mt-2 text-sm dark:text-untold-muted light:text-gray-500">Choose a new password for your account</p>
          <form onSubmit={handleSubmit} className="mt-8 space-y-4">
            <input
              type="password"
              required
              minLength={8}
              placeholder="New password (8+ chars)"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className={inputClass}
            />
            <input
              type="password"
              required
              minLength={8}
              placeholder="Confirm password"
              value={confirm}
              onChange={(e) => setConfirm(e.target.value)}
              className={inputClass}
            />
            {message && <p className="text-sm text-green-500">{message}</p>}
            {error && <p className="text-sm text-red-400">{error}</p>}
            <button type="submit" disabled={loading || !token} className="w-full py-3 rounded-xl bg-untold-gold text-untold-dark font-semibold disabled:opacity-60">
              {loading ? 'Updating…' : 'Update password'}
            </button>
          </form>
          <p className="mt-6 text-center text-sm dark:text-untold-muted light:text-gray-500">
            <Link to="/login" className="text-untold-gold font-medium">Back to sign in</Link>
          </p>
        </div>
      </section>
    </>
  );
}
