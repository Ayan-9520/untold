import { GoogleLogin, GoogleOAuthProvider } from '@react-oauth/google';
import { GOOGLE_CLIENT_ID } from '@/lib/constants';
import { useAuth } from './AuthProvider';
import { useState } from 'react';

function GoogleButton() {
  const { loginWithGoogle } = useAuth();
  const [error, setError] = useState<string | null>(null);

  if (!GOOGLE_CLIENT_ID) return null;

  return (
    <div className="space-y-2">
      <GoogleLogin
        onSuccess={async (res) => {
          if (!res.credential) return;
          try {
            setError(null);
            await loginWithGoogle(res.credential);
          } catch {
            setError('Google sign-in failed. Check Studio access or API config.');
          }
        }}
        onError={() => setError('Google sign-in was cancelled or failed.')}
        theme="filled_black"
        size="large"
        width="100%"
        text="continue_with"
        shape="rectangular"
      />
      {error && <p className="text-xs text-red-400 text-center">{error}</p>}
    </div>
  );
}

export default function GoogleLoginButton() {
  if (!GOOGLE_CLIENT_ID) {
    return (
      <p className="text-[10px] text-center text-studio-muted">
        Set VITE_GOOGLE_CLIENT_ID to enable Google login
      </p>
    );
  }

  return (
    <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
      <GoogleButton />
    </GoogleOAuthProvider>
  );
}
