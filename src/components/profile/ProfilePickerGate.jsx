import { useState } from 'react';
import { useWebAuth } from '../../context/WebAuthContext';
import { useViewerProfile } from '../../context/ViewerProfileContext';
import ProfilePicker from './ProfilePicker';

export default function ProfilePickerGate() {
  const { isAuthenticated } = useWebAuth();
  const { profiles, activeProfile } = useViewerProfile();
  const [dismissed, setDismissed] = useState(false);

  if (!isAuthenticated || dismissed || profiles.length <= 1) return null;

  const picked = sessionStorage.getItem('untold-profile-picked');
  if (picked && activeProfile) return null;

  return (
    <ProfilePicker
      onDone={() => {
        sessionStorage.setItem('untold-profile-picked', '1');
        setDismissed(true);
      }}
    />
  );
}
