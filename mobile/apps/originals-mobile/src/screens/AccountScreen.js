import React, { useState } from 'react';
import { TextInput, ActivityIndicator } from 'react-native';
import { loginWithApi, clearSession, getStoredUser } from '@untold/auth';
import { Screen, Title, Muted, PrimaryButton, colors } from '../components/ui';
import { registerPushToken } from '../lib/push';

export default function AccountScreen({ authApi, onAuthChange }) {
  const [user, setUser] = useState(null);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  React.useEffect(() => {
    getStoredUser().then(setUser);
  }, []);

  const login = async () => {
    setLoading(true);
    setError('');
    try {
      const me = await loginWithApi(authApi, email.trim(), password, { studio: false });
      await registerPushToken();
      setUser(me);
      onAuthChange?.(true);
    } catch (e) {
      setError(e.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    await clearSession();
    setUser(null);
    onAuthChange?.(false);
  };

  if (user) {
    return (
      <Screen>
        <Title>Account</Title>
        <Muted>{user.email || user.name}</Muted>
        <PrimaryButton title="Sign out" onPress={logout} />
      </Screen>
    );
  }

  return (
    <Screen>
      <Title>Sign in</Title>
      <Muted>Watchlist and personalized rows require an account.</Muted>
      <TextInput
        style={input}
        placeholder="Email"
        placeholderTextColor={colors.muted}
        autoCapitalize="none"
        value={email}
        onChangeText={setEmail}
      />
      <TextInput
        style={input}
        placeholder="Password"
        placeholderTextColor={colors.muted}
        secureTextEntry
        value={password}
        onChangeText={setPassword}
      />
      {error ? <Muted style={{ color: '#f87171' }}>{error}</Muted> : null}
      {loading ? (
        <ActivityIndicator color={colors.accent} style={{ marginTop: 16 }} />
      ) : (
        <PrimaryButton title="Sign in" onPress={login} />
      )}
    </Screen>
  );
}

const input = {
  backgroundColor: colors.card,
  borderWidth: 1,
  borderColor: colors.border,
  borderRadius: 10,
  padding: 14,
  color: colors.text,
  marginTop: 12,
};
