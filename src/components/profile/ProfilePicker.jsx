import { useState } from 'react';
import { useViewerProfile } from '../../context/ViewerProfileContext';
import { useWebAuth } from '../../context/WebAuthContext';

const AVATARS = ['🎬', '⚽', '🏏', '🥊', '🏆', '👤', '🧒'];

export default function ProfilePicker({ onDone }) {
  const { isAuthenticated } = useWebAuth();
  const { profiles, activeProfile, selectProfile, createProfile } = useViewerProfile();
  const [adding, setAdding] = useState(false);
  const [name, setName] = useState('');
  const [avatar, setAvatar] = useState('🎬');
  const [isKids, setIsKids] = useState(false);
  const [pin, setPin] = useState('');

  if (!isAuthenticated || profiles.length <= 1 && activeProfile) return null;

  const handleSelect = (profile) => {
    selectProfile(profile);
    onDone?.();
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    await createProfile({ name, avatar, is_kids: isKids, pin: isKids ? pin : undefined });
    setAdding(false);
    onDone?.();
  };

  return (
    <div className="profile-picker-overlay">
      <div className="profile-picker">
        <h2 className="font-display text-2xl font-bold text-white text-center mb-6">Who&apos;s watching?</h2>
        {!adding ? (
          <>
            <div className="flex flex-wrap justify-center gap-4 mb-6">
              {profiles.map((p) => (
                <button key={p.id} type="button" className="profile-picker-card" onClick={() => handleSelect(p)}>
                  <span className="text-4xl">{p.avatar}</span>
                  <span className="text-sm font-medium text-white mt-2">{p.name}</span>
                  {p.is_kids && <span className="text-[10px] text-untold-gold">Kids</span>}
                </button>
              ))}
              {profiles.length < 5 && (
                <button type="button" className="profile-picker-card profile-picker-card--add" onClick={() => setAdding(true)}>
                  <span className="text-3xl text-untold-muted">+</span>
                  <span className="text-sm text-untold-muted mt-2">Add Profile</span>
                </button>
              )}
            </div>
            {activeProfile && (
              <button type="button" className="w-full text-center text-sm text-untold-gold" onClick={onDone}>
                Continue as {activeProfile.name}
              </button>
            )}
          </>
        ) : (
          <form onSubmit={handleCreate} className="space-y-3 max-w-xs mx-auto">
            <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Profile name" required className="w-full rounded-lg px-3 py-2 text-sm dark:bg-black/40 border dark:border-untold-border" />
            <div className="flex gap-2 flex-wrap justify-center">
              {AVATARS.map((a) => (
                <button key={a} type="button" className={`text-2xl p-2 rounded-lg ${avatar === a ? 'bg-untold-gold/30' : ''}`} onClick={() => setAvatar(a)}>{a}</button>
              ))}
            </div>
            <label className="flex items-center gap-2 text-sm text-untold-muted">
              <input type="checkbox" checked={isKids} onChange={(e) => setIsKids(e.target.checked)} /> Kids profile (PIN optional)
            </label>
            {isKids && (
              <input value={pin} onChange={(e) => setPin(e.target.value)} placeholder="4-digit PIN" maxLength={6} className="w-full rounded-lg px-3 py-2 text-sm dark:bg-black/40 border dark:border-untold-border" />
            )}
            <div className="flex gap-2">
              <button type="button" onClick={() => setAdding(false)} className="flex-1 py-2 rounded-lg border dark:border-untold-border text-sm">Cancel</button>
              <button type="submit" className="flex-1 py-2 rounded-lg bg-untold-gold text-black text-sm font-semibold">Create</button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
