import { useState } from 'react';
import { Link } from 'react-router-dom';
import SEO from '../components/SEO';
import { api } from '../api/client';

export default function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const inputClass = `w-full rounded-xl px-4 py-3 text-sm outline-none border
    dark:bg-untold-surface dark:border-untold-border dark:text-untold-white
    light:bg-gray-50 light:border-gray-200 light:text-black focus:ring-2 focus:ring-untold-gold`;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setMessage('');
    try {
      const res = await api.auth.forgotPassword(email);
      setMessage(res.message || 'Check your email for a reset link.');
    } catch (err) {
      setError(err.response?.data?.detail || 'Unable to send reset email.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <SEO title="Forgot Password" description="Reset your UNTOLD password" path="/forgot-password" />
      <section className="pt-28 pb-16 min-h-[70vh] flex items-center">
        <div className="mx-auto w-full max-w-md px-4">
          <h1 className="font-display text-3xl font-bold dark:text-untold-white light:text-black">Forgot password</h1>
          <p className="mt-2 text-sm dark:text-untold-muted light:text-gray-500">We&apos;ll email you a reset link</p>
          <form onSubmit={handleSubmit} className="mt-8 space-y-4">
            <input
              type="email"
              required
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className={inputClass}
            />
            {message && <p className="text-sm text-green-500">{message}</p>}
            {error && <p className="text-sm text-red-400">{error}</p>}
            <button type="submit" disabled={loading} className="w-full py-3 rounded-xl bg-untold-gold text-untold-dark font-semibold disabled:opacity-60">
              {loading ? 'Sending…' : 'Send reset link'}
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
