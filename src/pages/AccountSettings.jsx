import { useEffect, useState } from 'react';
import { Link, Navigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import SEO from '../components/SEO';
import Button from '../components/ui/Button';
import { useWebAuth } from '../context/WebAuthContext';
import viewerApi from '../api/viewer';
import client from '../api/client';

export default function AccountSettingsPage() {
  const { t } = useTranslation();
  const { user, isAuthenticated, loading, logout } = useWebAuth();
  const [fullName, setFullName] = useState('');
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [prefs, setPrefs] = useState({ autoplay_next: true, default_quality: 'auto', subtitle_language: 'en', email_live_reminders: true });
  const [message, setMessage] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (user) setFullName(user.full_name || '');
    if (isAuthenticated) {
      viewerApi.getPreferences().then(setPrefs).catch(() => {});
    }
  }, [user, isAuthenticated]);

  if (loading) return null;
  if (!isAuthenticated) return <Navigate to="/login" state={{ from: { pathname: '/settings' } }} replace />;

  const saveProfile = async (e) => {
    e.preventDefault();
    setSaving(true);
    setMessage('');
    try {
      await client.patch('/users/me', { full_name: fullName });
      setMessage(t('settings.updated'));
    } catch (err) {
      setMessage(err.response?.data?.detail || t('settings.updated'));
    } finally {
      setSaving(false);
    }
  };

  const savePassword = async (e) => {
    e.preventDefault();
    setSaving(true);
    setMessage('');
    try {
      await client.post('/users/me/password', { current_password: currentPassword, new_password: newPassword });
      setCurrentPassword('');
      setNewPassword('');
      setMessage(t('settings.passwordChanged'));
    } catch (err) {
      setMessage(err.response?.data?.detail || t('settings.passwordChanged'));
    } finally {
      setSaving(false);
    }
  };

  const savePrefs = async () => {
    setSaving(true);
    try {
      await viewerApi.updatePreferences(prefs);
      setMessage(t('settings.savePrefs'));
    } catch {
      setMessage(t('settings.savePrefs'));
    } finally {
      setSaving(false);
    }
  };

  return (
    <>
      <SEO title={t('settings.title')} description={t('profile.settingsDesc')} path="/settings" />
      <section className="profile-page pt-28 pb-16">
        <div className="mx-auto max-w-2xl px-4 space-y-8">
          <div>
            <Link to="/profile" className="text-sm text-untold-gold hover:underline">← {t('nav.profile')}</Link>
            <h1 className="font-display text-3xl font-bold text-white mt-4">{t('settings.title')}</h1>
            <p className="text-sm text-untold-muted">{user.email}</p>
          </div>

          {message && <p className="text-sm text-untold-gold">{message}</p>}

          <form onSubmit={saveProfile} className="profile-header-card space-y-4">
            <h2 className="profile-section-title mb-0">{t('settings.profile')}</h2>
            <input value={fullName} onChange={(e) => setFullName(e.target.value)} className="w-full rounded-lg px-3 py-2 text-sm dark:bg-black/30 border dark:border-untold-border" />
            <Button type="submit" disabled={saving}>{t('settings.saveName')}</Button>
          </form>

          <form onSubmit={savePassword} className="profile-header-card space-y-4">
            <h2 className="profile-section-title mb-0">{t('settings.changePassword')}</h2>
            <input type="password" value={currentPassword} onChange={(e) => setCurrentPassword(e.target.value)} placeholder={t('settings.currentPassword')} className="w-full rounded-lg px-3 py-2 text-sm dark:bg-black/30 border dark:border-untold-border" />
            <input type="password" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} placeholder={t('settings.newPassword')} minLength={8} className="w-full rounded-lg px-3 py-2 text-sm dark:bg-black/30 border dark:border-untold-border" />
            <Button type="submit" variant="outline" disabled={saving}>{t('settings.updatePassword')}</Button>
          </form>

          <div className="profile-header-card space-y-4">
            <h2 className="profile-section-title mb-0">{t('settings.playbackPrefs')}</h2>
            <label className="flex items-center justify-between text-sm text-untold-muted">
              {t('settings.autoplayNext')}
              <input type="checkbox" checked={prefs.autoplay_next} onChange={(e) => setPrefs({ ...prefs, autoplay_next: e.target.checked })} />
            </label>
            <label className="flex items-center justify-between text-sm text-untold-muted">
              {t('settings.emailReminders')}
              <input type="checkbox" checked={prefs.email_live_reminders} onChange={(e) => setPrefs({ ...prefs, email_live_reminders: e.target.checked })} />
            </label>
            <label className="text-sm text-untold-muted block">
              {t('settings.defaultQuality')}
              <select value={prefs.default_quality} onChange={(e) => setPrefs({ ...prefs, default_quality: e.target.value })} className="w-full mt-1 rounded-lg px-3 py-2 dark:bg-black/30 border dark:border-untold-border">
                <option value="auto">Auto</option>
                <option value="1080">1080p</option>
                <option value="720">720p</option>
              </select>
            </label>
            <Button onClick={savePrefs} disabled={saving}>{t('settings.savePrefs')}</Button>
          </div>

          <div className="flex gap-3">
            <Link to="/billing" className="profile-action-btn profile-action-btn--gold">{t('profile.billing')}</Link>
            <button type="button" onClick={logout} className="profile-action-btn profile-action-btn--muted">{t('profile.signOut')}</button>
          </div>
        </div>
      </section>
    </>
  );
}
