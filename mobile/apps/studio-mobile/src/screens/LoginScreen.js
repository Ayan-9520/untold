import React, { useState } from 'react';
import { TextInput, ActivityIndicator } from 'react-native';
import { loginWithApi } from '@untold/auth';
import { Screen, Title, PrimaryButton, ErrorText, colors } from '../components/ui';
import { registerPushToken } from '../lib/push';

export default function LoginScreen({ authApi, onLoggedIn }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const submit = async () => {
    setLoading(true);
    setError('');
    try {
      const user = await loginWithApi(authApi, email.trim(), password, { studio: true });
      await registerPushToken('studio');
      onLoggedIn(user);
    } catch (e) {
      setError(e.response?.data?.detail || e.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Screen>
      <Title>UNTOLD Studio</Title>
      <TextInput
        style={input}
        placeholder="Email"
        placeholderTextColor={colors.muted}
        autoCapitalize="none"
        keyboardType="email-address"
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
      <ErrorText>{error}</ErrorText>
      {loading ? (
        <ActivityIndicator color={colors.accent} style={{ marginTop: 16 }} />
      ) : (
        <PrimaryButton title="Sign in" onPress={submit} />
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
  marginBottom: 12,
};
